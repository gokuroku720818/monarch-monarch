# 모나크모나크 V189 — 엘리베이터 수직 경로 복원

## 기준

- 기준 main commit: `09b6425566ab7cb6831d52cfb0fbf7b00f6b0d34`.
- V188 LITE Git blob: `dd5e3442c36bf4b7cd14377b8990379dfed534f7`.
- V188 FULL Git blob: `5a9e6081f43b8a0a8a7b85e4e82fc498b50afbdb`.
- 원본 `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`.
- 원본 ZIP SHA-256: `f3622ec468a9b0dfd160ecf8ae7292d1ce266020818131ec748ac54ed7ebc768`.
- 변경 범위는 이동/길찾기에서 원본 엘리베이터 타일 120..123의 같은 x/y 수직 z 이웃을 경로 그래프에 복원하는 한 가지 차이로 제한한다.

## V188에서 확인한 차이

V188의 `route()`와 `routeWithOriginalAiBlocks()`는 `CARD=[0,2,4,6]`만 순회한다. 따라서 같은 x/y에서 높이만 바뀌는 경로 edge가 없고, 실제 원본 맵의 엘리베이터 열을 위·아래 층 연결 통로로 사용할 수 없다.

실제 원본 맵 데이터 `M_014`에는 `(11,27,z)`에 다음 엘리베이터 열이 존재한다.

- z=8: 타일 120
- z=9..13: 타일 123
- z=14..15: 타일 122
- z=16: 타일 121

V188 실제 Chromium 엔진에서 z=8 병력으로 같은 x/y의 z=16을 목표로 `route()`를 호출하면 `null`이 반환된다.

## 원본 EXE 근거

`lm_win.exe` 경로 복원 루틴 `0x4425e1..0x442901`을 직접 역어셈블해 다음 분기를 확인했다.

- `0x442606`: 현재 유효 타일이 120(0x78)이면 같은 x/y의 `z+1` 후보를 검사한다.
- `0x442659`: 위쪽 후보가 선택되면 경로 방향 바이트에 `0xff`를 기록한다.
- `0x442677`: 현재 유효 타일이 121(0x79)이면 같은 x/y의 `z-1` 후보를 검사한다.
- `0x4426d5`: 아래쪽 후보가 선택되면 방향 바이트에 `0xfe`를 기록한다.
- `0x4426f9..0x442718`: 122(0x7a), 123(0x7b), 런타임 점유 오버레이 124(0x7c)는 양방향 수직 분기로 들어간다.
- `0x44271e..0x44278a`: `z+1`을 검사하고 선택 시 `0xff`를 기록한다.
- `0x44278a..0x4427f6`: `z-1`을 검사하고 선택 시 `0xfe`를 기록한다.
- `0x4427fb` 이후에야 수평 방향 0,2,4,6을 순서대로 검사한다.

따라서 수직 후보는 별도 특수 경로이며, 단순한 수평 4방향 이동으로 대체할 수 없다.

타일 124는 원본 런타임에서 병력이 지형 셀을 점유할 때 primary를 124로 바꾸고 원래 지형을 cell byte+1에 보존하는 표현이다. V188은 병력을 지형 배열과 분리해 보관하므로 원본 MAP의 124를 새 지형 규칙으로 임의 추가하지 않고, 실제 영구 엘리베이터 타일 120..123만 이번 경로 edge 대상으로 삼았다.

## 실패 우선 검증

`tests/test_vertical_elevator_route.js`는 `M_014`의 실제 120→123→122→121 열을 축약해 수평 우회를 완전히 막고 z=8에서 z=16까지 경로를 요구한다.

- V188 RED: `native elevator column must produce a route`, actual `null`.
- V189 GREEN: z=9..16의 8개 수직 step을 반환하고 각 특수 방향은 `0xff`.

실제 맵 브라우저 검증 `tests/test_vertical_elevator_route_browser.py`도 `M_014`의 원본 타일 열을 그대로 확인한다. V189에서는 첫 step이 `(11,27,9,dir=255)`이고 최종 step은 `(11,27,16)`이다. 실제 지형에는 중간 층에서 더 짧은 수평 경로가 존재할 수 있으므로, 테스트는 원본보다 강한 “끝까지 같은 열만 타야 한다” 조건을 강제하지 않는다.

## V189 수정

- `originalVerticalRouteSteps(x,y,z)`를 추가해 타일 120은 z+1, 121은 z-1, 122/123은 양쪽 z 이웃을 경로 후보로 제공한다.
- `route()`는 원본 순서처럼 수직 후보를 먼저, 그 다음 수평 0/2/4/6을 확장한다.
- `routeWithOriginalAiBlocks()`에도 동일한 수직 edge를 적용하되 기존 AI danger/block set 판정은 그대로 유지한다.
- `0xff/0xfe`는 수직 경로 sentinel이므로 병력의 화면 facing 방향으로 대입하지 않는다. 수직 step에서는 기존 facing을 유지한다.
- 이동 속도, 수평 방향 순서, `resolveStep()`, 전투, CPU 전략 선택, 경제/생산, 난수, 승패 규칙은 변경하지 않는다.

## 로컬 검증

- exact V188 blob gate로 생성한 V189 LITE Git blob: `fb7a8cb7b356a621be46f2b93e342d509e925cc0`.
- exact V188 blob gate로 생성한 V189 FULL Git blob: `1d15ecaf03bf57120058e46c028c6b6008d089bb`.
- V188 RED → V189 GREEN Node 회귀 확인.
- 실제 Chromium에서 V189 LITE/FULL 모두 M_014 수직 경로 성공, runtime/page error 0.
- V188의 Action 10 same-pass fence finish Node/Chromium 회귀 유지.
- `STAGES`, `SOUND_DATA`, 내장 Base64 payload 23개 바이트 동일.
- V189 LITE 75개 스테이지 × 각 10 simulation pass: 75/75, invariant/runtime/page error 0.
- LITE 4개, FULL 5개 인라인 JavaScript 블록 `node --check` 통과.

## 한계와 다음 우선순위

이번 변경은 원본 EXE에서 직접 확인된 **경로 복원 단계의 수직 엘리베이터 edge**만 복원한다. 원본의 distance-map 생성 전체와 각 AI 탐색기의 엘리베이터 비용/우선순위를 모두 동일하게 만들었다고 주장하지 않는다. 다음 이동/길찾기 대조에서는 원본 distance-map 생성 단계와 `resolveStep()` 희귀 높이/장애물 분기를 우선 확인하고, 그 뒤 전투로 넘어간다.
