import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("all_targets", Path(__file__).parents[2] / "tools/s179_all_target_router.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def test_cache_keeps_source_identity_and_config_and_reuses_only_exact_calls():
    from culinarystate.extraction.interfaces import SourceText
    class Base:
        def __init__(self): self.calls = 0
        def run(self, source, config, **kwargs): self.calls += 1; return (source.text_id, source.raw, config)
    base = Base(); cache = tool.CachedRung(base)
    a = SourceText.from_raw('A', 'Boil carrot.')
    assert cache.run(a, 'x', schema={}) == cache.run(a, 'x', schema={})
    assert base.calls == 1
    cache.run(SourceText.from_raw('B', a.raw), 'x', schema={})
    cache.run(a, 'different', schema={})
    assert base.calls == 3


def test_cached_router_matches_original_for_multiple_targets():
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.mechanism.router_demo import EvidenceIndex, route_text
    rung = RungA(); cache = tool.CachedRung(rung); index = EvidenceIndex({})
    for target in ['SVAR-000009', 'SVAR-000050']:
        a = route_text('Boil carrot for 5 minutes.', index=index, target_svar=target, rung=rung)
        b = route_text('Boil carrot for 5 minutes.', index=index, target_svar=target, rung=cache)
        assert a == b
