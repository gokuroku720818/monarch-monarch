# 모나크모나크 — V193 원본 패리티 복원판

원작 Windows 실행 파일·데이터·맵·효과음과 대조하며 개발 중인 비공식 HTML 복원판입니다. **V193도 아직 원작 전체의 장시간 동적 1:1 동일성을 주장하지 않습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V193 LITE 웹 기본판.
- `monarch_v193_lite.html`: 배포본과 바이트 동일한 V193 보관본.
- 원본 맵 75개와 WAV 효과음 159개 원본 바이트 검증을 유지합니다.
- BGM 포함 FULL HTML은 저장소에 커밋하지 않고 별도 완성 ZIP에 포함합니다.

## V193: 전투 금지 상태의 원본 action word 판독 복원

원본 `lm_win.exe 0x440a50..0x440a75`는 교전 전에 양쪽 유닛 구조체 `+0x10`의 **행동 워드 low byte**를 읽고 `0x11`이면 전투를 거부합니다. 브라우저용 보조 `state` 값은 이 판정의 원본 근거가 아닙니다.

V192는 `state & 0xff`를 사용해서 `state`와 `unitWord`가 어긋나는 경계에서 전투 허용/거부가 반대로 될 수 있었습니다. V193은 `unitWord & 0xff`를 사용하도록 복원했습니다.

Chromium RED/GREEN에서 `state=0x11, unitWord low=1`은 V192의 오거부에서 V193의 정상 교전으로, `state=1, unitWord low=0x11`은 V192의 오교전에서 V193의 정상 거부(return 5)로 바뀌는 것을 LITE/FULL 모두 확인했습니다.

V193 보고서: [V193_ORIGINAL_COMPARISON_REPORT.md](V193_ORIGINAL_COMPARISON_REPORT.md)

## V192: 치명타 이후 원본 반격·교환 종료 순서 복원

원본 `lm_win.exe 0x4409e5..0x440d0f`는 첫 타격과 반격 피해량을 미리 계산합니다. 그래서 첫 타격으로 방어 병력이 0이 되더라도 사망 처리 후 즉시 전투를 끝내지 않고, 기존 반격 금지/동결 조건이 없다면 **그 교환의 이미 계산된 반격을 수행**합니다.

V191은 방어자가 0이 되는 즉시 return 6으로 빠져 이 반격을 없앴고, 반대로 반격으로 공격자가 0이 되었을 때는 return 4를 냈습니다. V192는 원본 흐름대로 방어자 사망 뒤 반격 판정을 계속하고, 반격으로 공격자가 사망하면 return 6을 반환합니다.

Chromium RED/GREEN에서 800 대 10은 V191의 공격자 800 유지/return 6에서 V192의 공격자 799/return 4로, 10 대 800은 공격자 사망 시 return 4에서 return 6으로 교정됐습니다. LITE/FULL 모두 동일하게 검증했습니다.

V192 보고서: [V192_ORIGINAL_COMPARISON_REPORT.md](V192_ORIGINAL_COMPARISON_REPORT.md)

## V191: 원본 bounded reach 반경의 엄격한 상한 복원

원본 `lm_win.exe 0x43ef84`의 거리맵은 현재 거리에서 1을 더한 **새 후보 거리**를 반경 인자와 비교하고, `newDistance >= radius`이면 후보를 저장하지 않습니다. 따라서 반경 인자 3은 거리 0·1·2까지만 포함합니다.

V190의 `buildOriginalReachMap()`은 `d0>=radius`에서만 확장을 멈춰 거리 3 칸까지 저장했습니다. V191은 이를 `d0+1>=radius`로 맞춰 원본의 배타적 상한을 복원했습니다. 위/아래 승강기 분기와 일반 사방 확장 모두 원본에서 동일한 `JAE` 조건을 사용합니다.

Chromium RED/GREEN에서 M_000, 반경 3 기준 V190은 거리 3 칸이 7개 존재했고 V191은 최대 거리 2, 거리 3 칸 0개로 확인했습니다. V189 경로 동률 규칙과 V190 승강기 이동·탑승 회귀도 그대로 유지됩니다.

V191 보고서: [V191_ORIGINAL_COMPARISON_REPORT.md](V191_ORIGINAL_COMPARISON_REPORT.md)

## V190: 원본 승강기 수직 길찾기·탑승 복원

원본 `lm_win.exe`의 승강기는 단순한 높이 점프가 아닙니다. 타일 124의 **숨은 under-tile(120~123)** 을 보존하고, 거리맵에는 별도의 수직 up/down 상태를 만들며, 목표측 역추적에서 전용 경로 바이트 `0xFE/0xFF`를 사용합니다. 플랫폼 자체도 한 simulation pass마다 z 한 칸씩 움직이고 120/121 끝점에서 방향을 바꾼 뒤 30 pass 정지하며 탑승 병력을 함께 이동시킵니다.

V189에서는 이 별도 수직 분기가 아직 빠져 있어 원본 `M_014`의 (11,27,z=8..16) 승강기 축을 건널 수 없었습니다. V190은 V189의 CARD 동률 역추적을 유지하면서 **승강기 전용 거리맵·경로 재구성·움직이는 124 플랫폼·실제 탑승/하차**를 복원했습니다.

Chromium RED/GREEN에서 exact V189는 해당 경로가 `null`이고, V190은 8개의 `0xFE` 수직 단계를 포함한 경로를 만든 뒤 실제 병력이 승강기를 타고 z=8→16으로 이동해 상층 출구까지 도착하는 것을 확인했습니다. 75개 맵 × 10 pass 검사에서도 최대 4개 lift record와 visible 124 개수 invariant가 유지됩니다.

V190 보고서: [V190_ORIGINAL_COMPARISON_REPORT.md](V190_ORIGINAL_COMPARISON_REPORT.md)

## V189: 최단경로 동률 시 원본의 목표측 역추적 순서 복원

원본 `lm_win.exe`는 출발점에서 거리맵을 만든 뒤, 목표점에서 출발점 방향으로 `0,2,4,6`(서→북→동→남)을 조사해 **거리값이 엄격히 더 작은 칸만** 선택하며 경로 바이트를 역구성합니다. V188은 BFS에서 처음 발견한 predecessor를 그대로 경로로 사용했기 때문에 최단거리 길이는 같아도 대칭 우회 상황의 실제 경로 모양이 원본과 달랐습니다.

V189는 `originalCardinalBacktrack()`을 추가해 일반 이동, AI block 경로, AI reach-map 경로가 모두 원본 `0x4424e0 / 0x4427fb` 방식으로 목표측에서 역추적하도록 맞췄습니다. 4×4 평지의 단일 장애물 회귀에서 원본과 동일한 좌측→하단 우회와 방향 바이트 `6,6,6,4,4,4`를 Chromium 실제 엔진에서 확인했습니다.

V189 보고서: [V189_ORIGINAL_COMPARISON_REPORT.md](V189_ORIGINAL_COMPARISON_REPORT.md)

## V188: 울타리 제거와 Action 10 종료를 같은 패스에서 처리

원본 `lm_win.exe`의 Action 10 worker는 마지막 울타리 코어/캡을 실제로 제거하면 return 0을 내고, dispatcher는 return 3이 아닌 경우 **그 같은 처리 pass에서 바로 완료/계속작업 handler**로 들어갑니다.

V187은 울타리를 제거한 뒤 Action 10이 한 simulation pass 더 남았다가 다음 pass에서 정리됐습니다. V188은 정확한 target 셀이 0이 된 즉시 `finishWorkAction()`을 실행해 원본 return-code 흐름과 맞춥니다.

Chromium LITE/FULL에서 구조물이 실제로 사라진 동일 pass에 actionCode가 10에서 해제되고 target이 null이 되는 것을 확인했고, V187의 자기 기지 제외 회귀도 그대로 통과했습니다.

V188 보고서: [V188_ORIGINAL_COMPARISON_REPORT.md](V188_ORIGINAL_COMPARISON_REPORT.md)

## V187: 연속 생산기지 파괴에서 자기 기지 제외

원본 `lm_win.exe 0x43e90f..0x43e96a`의 Action 8 반복작업 wrapper는 tile 29..32를 후보로 만든 뒤, 현재 faction의 자기 생산기지 `29+faction`만 후보 비트에서 제거합니다.

V186는 29..32를 전부 후보로 받아서 연속 파괴가 자기 기지까지 다음 목표로 선택할 수 있었습니다. V187은 원본 흐름대로 **자기 기지는 건너뛰고 적 생산기지만 계속 파괴 대상으로 유지**합니다.

Chromium 실제 엔진에서 탐색 우선 위치에 자기 기지(tile 29), 그 반대편에 적 기지(tile 30)를 배치했을 때 자기 기지를 건너뛰고 적 기지를 Action 8 목표로 선택하는 것을 LITE/FULL 모두 확인했습니다.

V187 보고서: [V187_ORIGINAL_COMPARISON_REPORT.md](V187_ORIGINAL_COMPARISON_REPORT.md)

## V186: 계속건설 중 자금 부족 대기

원본 `lm_win.exe`는 생산기지 계속작업에서 **다음 목표 선택과 실제 자금 100 차감을 서로 다른 단계**에서 처리합니다. 목표 탐색기 `0x43e8bb → 0x43eb4c`는 자금을 보지 않고, 실제 작업 셀에서만 `0x430640`이 100을 지불합니다. 자금이 부족하면 worker가 return 1로 빠지고 Action 4는 유지되어 다음 pass에서 재시도합니다.

V185는 자금 100 미만이면 다음 목표 자체를 찾지 않았고, 이미 Action 4여도 건설 실패 시 연속작업을 끝냈습니다. V186는 원작 흐름에 맞춰:

- 자금 100 미만이어도 다음 기지 목표를 선택
- 해당 위치에서 자금이 부족하면 Action 4와 target 유지
- 자금이 100이 되면 같은 목표를 건설
- 이후 계속건설 흐름 유지

Chromium에서 **99 자원 대기 → 100 자원에서 실제 건설 → 자원 0/병력 감소 → 다음 Action 4 목표 획득**까지 확인했습니다.

V186 보고서: [V186_ORIGINAL_COMPARISON_REPORT.md](V186_ORIGINAL_COMPARISON_REPORT.md)

## V185: 마지막 병력 1 계속건설

V185는 원본 반복 탐색기가 병력 필드를 검사하지 않는 흐름과 실제 건설의 최소 작업량 1을 반영해, 병력 1인 계속건설 부대가 마지막 기지 목표를 한 번 더 잡을 수 있도록 복원했습니다.

V185 보고서: [V185_ORIGINAL_COMPARISON_REPORT.md](V185_ORIGINAL_COMPARISON_REPORT.md)

## V184: 정확한 울타리 파괴 높이

원본 M_032의 같은 x/y 열에 존재하는 z=3, z=38 울타리 중 선택한 정확한 z만 Action 10이 처리하도록 복원했습니다. 높은 울타리가 사라진 뒤 낮은 울타리로 자동 재타깃하지 않습니다.

V184 보고서: [V184_ORIGINAL_COMPARISON_REPORT.md](V184_ORIGINAL_COMPARISON_REPORT.md)

## 원본 패리티 하네스

`parity/original-parity.json`에서 규칙을 `CONFIRMED / PARTIAL / UNKNOWN / BROWSER_ADAPTATION`으로 관리하고, `tools/audit_parity.py`가 근거·구현 심볼·테스트 연결을 검사합니다.

설계: [Original-Parity Restoration Design](docs/superpowers/specs/2026-09-28-monarch-original-parity-design.md)

## V193 검증 범위

GitHub Actions run `36654140042`에서 다음 게이트가 모두 통과했습니다.

- 원본 75 MAP, 제목·장군 마커, WAV 159개
- V173~V188 focused regressions
- V193 native action-word combat gate RED/GREEN Chromium regression
- V192 lethal-hit retaliation/return-code RED/GREEN Chromium regression
- V191 strict bounded reach RED/GREEN Chromium regression
- V189 목표측 route tie backtrack Node/Chromium regression
- V190 승강기 경로·플랫폼·실제 탑승 Chromium regression
- V188 same-pass 울타리 종료 Chromium regression
- V187 자기 기지 제외 Chromium regression
- V192→V193 역패치 전체 바이트 동일성
- STAGES/SOUND_DATA 및 Base64 23개 동일
- 75개 스테이지 × 10 simulation pass invariant smoke
- JavaScript syntax 및 배포 archive identity

테스트된 V193 LITE Git blob: `ec7dc0a2cef14fa575ccfc4207cbd2431c372387`.

## 이전 수정

- V193: 전투 금지 상태 0x11을 원본처럼 action word low byte에서 판독.
- V192: 치명타 방어자의 같은 교환 반격 유지 및 반격으로 공격자 사망 시 return 6 복원.
- V191: bounded reach-map의 반경을 원본처럼 배타적 상한으로 처리.
- V190: 승강기 수직 길찾기·이동 플랫폼·탑승 복원.
- V188: 울타리 제거와 Action 10 종료를 같은 simulation pass에서 처리.
- V187: 연속 생산기지 파괴에서 자기 진영 생산기지 제외.
- V186: 계속건설 중 자금 부족 시 목표 유지 및 자금 회복 후 재시도.
- V185: 병력 1인 계속건설 부대의 마지막 생산기지 목표 허용.
- V184: Action 10의 정확한 울타리 z 타깃 유지.
- V183: DF100 완성 다리의 무효 수리 명령 차단.
- V182: 울타리 작업 가능 조건과 명령 활성화 조건 일치.
- V181: 파괴/작업 명령의 지형 높이와 실제 작업 위치 일치.
- V180: 명령 중 시뮬레이션 일시정지.
- V179: 울타리 건설 위치 선택.
- V178: 높은 지형의 다리 상판 높이 판정.

## 아직 남은 원작 대조

이동/길찾기 추가 세부 규칙, 전투, 생산·세금·경제, CPU AI, 중립 AI, 난수·타이밍, 승패·점수, 원본 Windows UI/입력을 영역별로 계속 원본 EXE와 대조합니다. 비용이 드는 외부 서버는 사용하지 않고, 원본 EXE 정적 분석 + 원본 데이터 + Chromium + GitHub Actions로 계속 복원합니다.
