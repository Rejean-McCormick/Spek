# Editorial composition and failed-private-preview cleanup — Branch 04 final-system integration

**Scope:** `TARGET_DESIGN` plus named local tests; not a public release, current Git HEAD or production assertion.

Spek 0.5.0 is an autonomous multilingual editorial product. It accepts typed units and approved short realizations and may call SemantiK's public CLI with an explicit request mapping, but it neither certifies GF/PGF runtimes nor approves facts or publishes automatically. `spek.slot-dialogue/1.0` is a **private plan** of allowed language forms; missing obligations and unsupported grammar fail closed.

**Implemented safety correction:** `spek/semantik_execution.py::realize_mapping` now deletes its temporary private staging directory on **any failed** realization or transfer. This prevents residual typed semantic requests/results after a failed render. Successful output still returns `private_work_dir` for explicit local review; callers must clean it when finished. `tests/test_semantik_execution.py` covers both behaviors. This change does not add a publication gate or a new SemantiK API.

**Owner handoff:** the current SA request schema exposes communicative force and supported block kinds, not arbitrary long-form rhetorical generation. A dedicated v11-derived-view→SemantiK ACL is **TBD** and cannot be invented here. An editor may publish a Spek artifact only under a separately authorized target and license/privacy review.

