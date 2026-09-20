# 모나크모나크 V177 — 장군 패배 시 유효하지 않은 명령 UI 정리

## 원본 및 기준
- V176 GitHub Pages `index.html` Git blob: `012c19c5505ac5a3f46b4dd73a0d9e965cae530a`.
- 원작 Windows 파일에서 추출해 검증한 75개 MAP 지형·스테이지 제목·장군 위치, WAV 159개 바이트는 V177에서도 보존한다.
- AI/전투/경제/승패의 원본 동작은 고치거나 임의로 추가하지 않는다.

## 재현된 V176 오류
M_000에서 아군 장군을 선택해 왕 명령 패널을 연 후, 아군 일반 병력과 생산기지를 모두 제거하여 실제 시뮬레이션 `update(1)`이 `refreshFactionElimination()`에서 장군을 죽이도록 한다. 엔진의 기존 처리 `selected.forEach(i=>{if(units[i]===k)selected.delete(i)})`는 선택을 직접 지우지만 명령 UI에 알리지 않는다. 이 때문에 `selected=[]`, `king.alive=false`인데 `originalCommandPanel.show`와 `uiPhase=king`이 남았다.

## V177 수정
- 장군이 실제로 선택에서 제거됐을 때만 기존 `__MONARCH_RECONCILE_SELECTION__(true)` 함수를 호출한다.
- 다른 부대를 선택했거나 장군이 선택되지 않았다면 패널을 임의로 닫지 않는다.
- 명령 UI 외의 원작 패배·영토·부대 생성·전투·경제 규칙과 원본 맵·그래픽·WAV 데이터는 건드리지 않는다.

## 검증
- Chromium 실제 시뮬레이션 재현: V176은 테스트 실패, V177 경량판·배경음악 포함판 각각 통과.
- 슬롯 재사용, 터치 포커스 복구, 터치 드래그 선행 회귀 테스트 통과.
- 원본 MAP 75개(지형/제목/장군 마커), WAV 159개 SHA-256 보존 검사 양쪽 통과.
- JavaScript 구문: 경량판 4블록 / 전체판 5블록 통과.
- GitHub Actions `tests/test_king_defeat_cleanup.js`는 출하 HTML의 장군 패배 처리 구문을 추출해 실제 실행한다.

## 제한
GitHub Pages는 배경음악 제외 경량판이다. 전체판 HTML에는 기존 13곡 자산을 보존한다. 전체 게임을 원작 Windows EXE와 동일 입력으로 장시간 1:1 대조한 것은 아니므로, 게임 전체 동일성을 입증한 것으로 해석하면 안 된다.
