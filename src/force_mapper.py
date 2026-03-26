from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from src.load_combiner import LoadCombiner


@dataclass
class ForcePoint:
    angle: float
    force: Dict[str, Dict[str, float]]
    raw: Dict[str, Any]


class ForceMapper:
    """
    内力映射器
    将全环角度-内力数据切片到 3A+2B+1C 分块，并生成可用于优化器的 ForceEnvelope。
    """

    def __init__(self, safety_level: int = 2):
        self.combiner = LoadCombiner(safety_level=safety_level)

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        return angle % 360.0

    @staticmethod
    def _angle_in_range(angle: float, start: float, end: float) -> bool:
        a = angle % 360.0
        s = start % 360.0
        e = end % 360.0
        if s <= e:
            return s <= a <= e
        return a >= s or a <= e

    @staticmethod
    def _get_segment_attr(seg: Any, name: str, fallback: Optional[str] = None):
        if hasattr(seg, name):
            return getattr(seg, name)
        if isinstance(seg, dict) and name in seg:
            return seg[name]
        if fallback and isinstance(seg, dict) and fallback in seg:
            return seg[fallback]
        return None

    def _get_segment_type(self, seg: Any, seg_id: Optional[str]) -> Optional[str]:
        stype = self._get_segment_attr(seg, 'segment_type', 'type')
        if stype is not None:
            return str(stype)
        if seg_id:
            head = str(seg_id).strip()[:1].upper()
            if head in ('A', 'B', 'C'):
                return head
        return None

    @staticmethod
    def _envelope_score(envelope: List[Dict[str, Any]]) -> tuple:
        if not envelope:
            return (float('-inf'), float('-inf'), float('-inf'))
        max_m = 0.0
        max_n = 0.0
        max_v = 0.0
        for forces in envelope:
            for field in ('design', 'quasi'):
                payload = forces.get(field, {})
                max_m = max(max_m, abs(payload.get('M', 0.0)))
                max_n = max(max_n, abs(payload.get('N', 0.0)))
                max_v = max(max_v, abs(payload.get('V', 0.0)))
        # 主序: |M|, 次序: |N|, 再次: |V|
        return (max_m, max_n, max_v)

    @staticmethod
    def _build_refs(envelopes: List[List[Dict[str, Any]]]) -> Dict[str, float]:
        refs = {
            'dN': 1.0, 'dM': 1.0, 'dV': 1.0,
            'qN': 1.0, 'qM': 1.0, 'qV': 1.0,
        }
        for env in envelopes:
            for force in env:
                d = force.get('design', {})
                q = force.get('quasi', {})
                refs['dN'] = max(refs['dN'], abs(d.get('N', 0.0)))
                refs['dM'] = max(refs['dM'], abs(d.get('M', 0.0)))
                refs['dV'] = max(refs['dV'], abs(d.get('V', 0.0)))
                refs['qN'] = max(refs['qN'], abs(q.get('N', 0.0)))
                refs['qM'] = max(refs['qM'], abs(q.get('M', 0.0)))
                refs['qV'] = max(refs['qV'], abs(q.get('V', 0.0)))
        return refs

    @staticmethod
    def _control_score(envelope: List[Dict[str, Any]], refs: Dict[str, float]) -> tuple:
        """
        以 ULS/SLS/抗剪控制相关的内力组合强度评分。
        返回值越大表示越不利。
        """
        if not envelope:
            return (float('-inf'), float('-inf'), float('-inf'), float('-inf'))

        worst_combo = 0.0
        worst_uls = 0.0
        worst_sls = 0.0
        max_v = 0.0
        for force in envelope:
            d = force.get('design', {})
            q = force.get('quasi', {})
            uls_idx = (
                (abs(d.get('N', 0.0)) / refs['dN']) ** 2 +
                (abs(d.get('M', 0.0)) / refs['dM']) ** 2 +
                (abs(d.get('V', 0.0)) / refs['dV']) ** 2
            ) ** 0.5
            sls_idx = (
                (abs(q.get('N', 0.0)) / refs['qN']) ** 2 +
                (abs(q.get('M', 0.0)) / refs['qM']) ** 2 +
                (abs(q.get('V', 0.0)) / refs['qV']) ** 2
            ) ** 0.5
            combo = max(uls_idx, sls_idx)
            worst_combo = max(worst_combo, combo)
            worst_uls = max(worst_uls, uls_idx)
            worst_sls = max(worst_sls, sls_idx)
            max_v = max(max_v, abs(d.get('V', 0.0)))

        # 主序: 组合控制强度；次序: ULS；再次: SLS；再 tie-break: |V|
        return (worst_combo, worst_uls, worst_sls, max_v)

    def _ensure_force_payload(self, record: Dict[str, Any]) -> Dict[str, Any]:
        force = {
            'design': dict(record['design']),
            'quasi': dict(record['quasi'])
        }
        if 'V' not in force['design']:
            force['design']['V'] = 0.0
        if 'V' not in force['quasi']:
            force['quasi']['V'] = 0.0
        force['gamma_d'] = record.get('gamma_d', 1.0)
        return force

    def _combine_components(self, components: Dict[str, Dict[str, float]], gamma_d: Optional[float]) -> Dict[str, Any]:
        payload = self.combiner.calculate_loads(components)

        # 可选：若输入包含剪力 V，则按相同系数组合
        has_v = False
        for key in ('self_weight', 'earth_pressure', 'live_load'):
            if 'V' in components.get(key, {}):
                has_v = True
                break
        if has_v:
            v_earth = components.get('earth_pressure', {}).get('V', 0.0)
            v_self = components.get('self_weight', {}).get('V', 0.0)
            v_live = components.get('live_load', {}).get('V', 0.0)
            v_design = self.combiner.gamma_0 * (
                self.combiner.gamma_G_self * v_self +
                self.combiner.gamma_G_earth * v_earth +
                self.combiner.gamma_Q * v_live
            )
            v_quasi = (
                1.0 * v_self +
                1.0 * v_earth +
                self.combiner.psi_q_live * v_live
            )
            payload['design']['V'] = v_design
            payload['quasi']['V'] = v_quasi

        if gamma_d is not None:
            payload['gamma_d'] = gamma_d

        return payload

    def normalize_records(self, records: Iterable[Dict[str, Any]]) -> List[ForcePoint]:
        """
        标准化内力记录
        注意: ANSYS数据使用新坐标系(0°=拱底),需转换为内部坐标系(0°=右侧)
        转换公式: 内部角度 = (ANSYS角度 - 90°) mod 360°
        """
        points: List[ForcePoint] = []
        for rec in records:
            angle = rec.get('angle', rec.get('theta'))
            if angle is None:
                raise ValueError('force record missing angle/theta')

            # 坐标系转换: ANSYS(0°=拱底) -> 内部(0°=右侧)
            angle_internal = (float(angle) - 90.0) % 360.0

            if 'design' in rec and 'quasi' in rec:
                force = self._ensure_force_payload(rec)
            else:
                components = rec.get('components')
                if components is None:
                    components = {
                        'self_weight': rec.get('self_weight', {}),
                        'earth_pressure': rec.get('earth_pressure', {}),
                        'live_load': rec.get('live_load', {})
                    }
                force = self._combine_components(components, rec.get('gamma_d'))

            points.append(ForcePoint(
                angle=self._normalize_angle(angle_internal),
                force=force,
                raw=rec
            ))

        return points

    def _select_extremes(self, points: List[ForcePoint]) -> List[ForcePoint]:
        if not points:
            return []

        idx_set = set()
        for field in ('design', 'quasi'):
            for key in ('N', 'M'):
                values = [p.force[field][key] for p in points]
                max_idx = max(range(len(values)), key=lambda i: values[i])
                min_idx = min(range(len(values)), key=lambda i: values[i])
                idx_set.add(max_idx)
                idx_set.add(min_idx)

        return [points[i] for i in sorted(idx_set)]

    def _select_topk_by_abs_m(self, points: List[ForcePoint], top_k: int) -> List[ForcePoint]:
        if top_k <= 0:
            return []

        idx_set = set()
        for field in ('design', 'quasi'):
            values = [abs(p.force[field]['M']) for p in points]
            ranked = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
            for i in ranked[:top_k]:
                idx_set.add(i)

        return [points[i] for i in sorted(idx_set)]

    def reduce_envelope(self, points: List[ForcePoint], mode: str = 'all', top_k: int = 0) -> List[Dict[str, Any]]:
        if mode == 'all' or len(points) <= 1:
            return [p.force for p in points]

        if mode == 'extreme':
            picked = self._select_extremes(points)
            if top_k > 0:
                picked.extend(self._select_topk_by_abs_m(points, top_k))
            # 去重
            unique = []
            seen = set()
            for p in picked:
                key = id(p)
                if key in seen:
                    continue
                seen.add(key)
                unique.append(p)
            return [p.force for p in unique]

        raise ValueError(f'unsupported reduce mode: {mode}')

    def map_segments(self, segments: Iterable[Any], records: Iterable[Dict[str, Any]], mode: str = 'all', top_k: int = 0) -> Dict[str, List[Dict[str, Any]]]:
        points = self.normalize_records(records)
        results: Dict[str, List[Dict[str, Any]]] = {}

        for seg in segments:
            seg_id = self._get_segment_attr(seg, 'segment_id', 'id')
            if seg_id is None:
                raise ValueError('segment missing segment_id/id')
            start = self._get_segment_attr(seg, 'start_angle')
            end = self._get_segment_attr(seg, 'end_angle')
            if start is None or end is None:
                raise ValueError(f'segment {seg_id} missing start_angle/end_angle')

            bucket = [p for p in points if self._angle_in_range(p.angle, start, end)]
            results[str(seg_id)] = self.reduce_envelope(bucket, mode=mode, top_k=top_k)

        return results

    def map_segments_symmetric(self, segments: Iterable[Any], records: Iterable[Dict[str, Any]], mode: str = 'all', top_k: int = 0) -> Dict[str, Dict[str, Any]]:
        """
        对称设计模式：
        - 仍保留每个分块的完整内力包络 (by_segment)
        - 同类型分块 (A/B/C) 仅选取“内力最大”的那一块作为设计代表 (symmetric)
        - 返回 type_source 用于追踪选取的分块来源
        """
        per_segment = self.map_segments(segments, records, mode=mode, top_k=top_k)

        # 建立 type -> [(seg_id, envelope), ...]
        type_groups: Dict[str, List[tuple]] = {}
        seg_meta: List[tuple] = []
        for seg in segments:
            seg_id = self._get_segment_attr(seg, 'segment_id', 'id')
            if seg_id is None:
                raise ValueError('segment missing segment_id/id')
            seg_id = str(seg_id)
            seg_type = self._get_segment_type(seg, seg_id)
            if seg_type is None:
                raise ValueError(f'segment {seg_id} missing segment_type/type and cannot infer from id')
            envelope = per_segment.get(seg_id, [])
            seg_meta.append((seg_id, seg_type, envelope))
            type_groups.setdefault(seg_type, []).append((seg_id, envelope))

        # 选择每个类型的代表块（最大内力）
        type_source: Dict[str, str] = {}
        type_envelope: Dict[str, List[Dict[str, Any]]] = {}
        for stype, items in type_groups.items():
            refs = self._build_refs([env for _sid, env in items])
            best_id = None
            best_env = []
            best_score = (float('-inf'), float('-inf'), float('-inf'), float('-inf'))
            for seg_id, env in items:
                score = self._control_score(env, refs)
                if score > best_score:
                    best_score = score
                    best_id = seg_id
                    best_env = env
            if best_id is not None:
                type_source[stype] = best_id
                type_envelope[stype] = best_env

        # 生成对称设计映射：同类型使用同一包络
        symmetric: Dict[str, List[Dict[str, Any]]] = {}
        for seg_id, seg_type, _env in seg_meta:
            symmetric[seg_id] = type_envelope.get(seg_type, [])

        return {
            'by_segment': per_segment,
            'symmetric': symmetric,
            'type_source': type_source
        }
