# 모나크모나크 — V200 원본 패리티 복원판

원작 Windows 실행 파일·데이터·맵·효과음과 대조하며 개발 중인 비공식 HTML 복원판입니다. **V200도 아직 원작 전체의 장시간 동적 1:1 동일성을 주장하지 않습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V200 LITE 웹 기본판.
- `monarch_v200_lite.html`: 배포본과 바이트 동일한 V200 보관본.
- 원본 맵 75개와 WAV 효과음 159개 원본 바이트 검증을 유지합니다.
- BGM 포함 FULL HTML은 저장소에 커밋하지 않고 별도 완성 ZIP에 포함합니다.

## V200: CPU 적 장군 표적 스캔의 원본 0x0800 판정 복원

원본 `lm_win.exe 0x43dad4..0x43db8f`은 도달 가능한 다른 세력 유닛을 적 후보로 저장하며, **성 HP를 확인해 장군을 제외하는 분기가 없습니다.** 그리고 슬롯 스캔을 즉시 끝내는 조건은 candidate action word의 `0x0800` 비트뿐입니다.

V199에는 `type==='king' && castleHP>0` 후보 제외와 `type==='king'` 조기 종료가 추가돼 있었습니다. V200은 이 브라우저 전용 조건을 제거해 원본 스캔으로 맞췄습니다.

Chromium RED/GREEN에서 성 HP 400인 native-bit 장군은 V199의 오제외에서 V200의 정상 표적으로 교정됐고, `type='king'`이지만 0x0800이 없는 앞 슬롯보다 뒤의 실제 0x0800 장군을 선택하는 것도 확인했습니다.

V200 보고서: [V200_ORIGINAL_COMPARISON_REPORT.md](V200_ORIGINAL_COMPARISON_REPORT.md)

## V199: CPU 아군 합류 대상의 원본 action word 판독 복원

원본 `lm_win.exe 0x43de38..0x43de6b`은 아군 합류 후보의 행동 2/16을 브라우저 보조값이 아니라 유닛 구조체 `+0x10`의 **packed action word low byte**에서 읽습니다. 행동 2인 후보는 제외하고, 행동 16인 후보는 슬롯 스캔 중 즉시 우선 선택합니다.

V198은 별도 `actionCode`를 사용해 두 값이 어긋나는 경계에서 잘못된 대상을 고를 수 있었습니다. V199은 두 판정을 모두 `unitWord & 0xff`로 복원했습니다.

Chromium RED/GREEN에서 native word가 2이지만 `actionCode=1`인 후보는 V198의 오선택에서 V199의 정상 제외로, native word가 16이지만 `actionCode=1`인 집결 후보는 V198의 우선권 누락에서 V199의 즉시 우선 선택으로 교정됐습니다.

V199 보고서: [V199_ORIGINAL_COMPARISON_REPORT.md](V199_ORIGINAL_COMPARISON_REPORT.md)

## V198: 반격 계산값 0의 원본 피해 처리 복원

원본 `lm_win.exe`는 첫 타격과 반격의 최소 피해 분기가 서로 다릅니다. 첫 타격 `0x440b77..0x440b84`는 계산값이 0 이하이면 1로 올리지만, 반격 `0x440c76..0x440c83`은 **정확히 0이면 그대로 0**을 유지하고 음수일 때만 1로 올립니다.

V197은 공통 `Math.max(1,...)` helper를 사용해 반격 계산값 0도 피해 1로 만들었습니다. V198은 first-strike/retaliation clamp를 원본처럼 분리했습니다.

Chromium RED/GREEN에서 공격자 strength 80, z=5 / 반격자 strength 100, z=4 조건에서 첫 타격은 2로 유지되고, 반격은 V197의 1 피해에서 V198의 0 피해로 교정됐습니다.

V198 보고서: [V198_ORIGINAL_COMPARISON_REPORT.md](V198_ORIGINAL_COMPARISON_REPORT.md)

## V197: 아군 병합의 장군 판정 원본 비트 복원

원본 `lm_win.exe 0x440d5c..0x440d98`의 아군 병합 helper는 브라우저의 `type='king'` 같은 보조 라벨을 보지 않고, 양쪽 유닛 행동 워드 `+0x10`의 **0x0800 장군 비트만** 검사합니다.

V196은 `type==='king'`도 별도로 병합 금지 조건에 포함해, 보조 라벨과 원본 행동 워드가 어긋난 경계에서 원작보다 넓게 병합을 막았습니다. V197은 이 브라우저 전용 조건을 제거하고 원본 0x0800 비트를 단일 근거로 사용합니다.

Chromium RED/GREEN에서 `type='king'`이지만 0x0800 비트가 없는 actor/target은 V196의 병합 거부에서 V197의 정상 병합으로 교정됐고, 반대로 `type='soldier'`라도 0x0800 비트가 있으면 계속 병합을 거부하는 것을 확인했습니다.

V197 보고서: [V197_ORIGINAL_COMPARISON_REPORT.md](V197_ORIGINAL_COMPARISON_REPORT.md)

## V196: 사망 중 점유 슬롯의 접촉 차단 복원

원본은 병력이 사망 상태에 들어가도 사망 애니메이션이 끝나 슬롯이 실제 해제되기 전까지 그 슬롯을 점유된 것으로 취급합니다. 적 접촉 경로 `0x440a77..0x440a93`과 아군 합류 경로 `0x440d19..0x440d37` 모두 death flag `0x4`를 확인하고 return 5로 접촉을 막습니다.

V195는 브라우저의 `alive=false`만 보고 `exchange()` 초입에서 return 0을 해 사망 중 슬롯을 빈칸처럼 취급할 수 있었습니다. V196은 접촉 대상의 `alive` 조기 종료를 제거하고, 원본 death flag 판정까지 진행하게 복원했습니다.

Chromium RED/GREEN에서 적·아군 사망 중 슬롯 모두 `stepCellContact()`가 실제 점유자를 찾는 상태에서 V195 return 0 → V196 return 5로 교정됐고, 공격 병력 수치는 변하지 않았습니다.

V196 보고서: [V196_ORIGINAL_COMPARISON_REPORT.md](V196_ORIGINAL_COMPARISON_REPORT.md)

## V195: 장군 판정의 원본 0x0800 비트 복원

원본 `lm_win.exe 0x440b55..0x440b70`는 첫 타격 시 장군 고정 피해 100 여부를 **유닛 행동 워드의 0x0800 비트만** 보고 판정합니다. 브라우저의 `type='king'` 문자열은 원본 판정 근거가 아닙니다.

V194는 `unitWord & 0x0800` 또는 `type==='king'` 중 하나만 맞아도 장군으로 처리했습니다. V195는 원본처럼 0x0800 비트 하나만 사용합니다.

Chromium RED/GREEN에서 `type='king'`이지만 0x0800 비트가 없는 유닛은 V194의 고정 100 피해에서 V195의 정상 피해 10으로 교정됐고, `type='soldier'`라도 0x0800 비트가 있으면 100 피해가 그대로 유지됐습니다. LITE/FULL 모두 확인했습니다.

V195 보고서: [V195_ORIGINAL_COMPARISON_REPORT.md](V195_ORIGINAL_COMPARISON_REPORT.md)

## V194: 전투 사망 효과음의 타격자 세력 선택 복원

원본 `lm_win.exe 0x436217..0x436233`은 세력 효과음 인덱스 테이블을 0,1,2,3,4로 초기화하고, 전투 사망 시 죽은 유닛이 아니라 **치명타를 가한 쪽의 세력**으로 LM0030~LM0034를 선택합니다.

V193은 피해자 세력을 사용했습니다. V194는 첫 타격으로 방어자가 죽으면 공격자 세력, 반격으로 공격자가 죽으면 반격자 세력을 사용하도록 원본 흐름에 맞췄습니다.

Chromium에서 세력 0이 세력 1을 쓰러뜨릴 때 V193의 LM0031 → V194의 LM0030, 세력 1의 반격으로 세력 0이 죽을 때 LM0030 → LM0031로 교정되는 것을 실제 내장 WAV payload로 LITE/FULL 모두 확인했습니다.

V194 보고서: [V194_ORIGINAL_COMPARISON_REPORT.md](V194_ORIGINAL_COMPARISON_REPORT.md)

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

## V200 검증 범위

GitHub Actions run `36660010544`에서 다음 게이트가 모두 통과했습니다.

- 원본 75 MAP, 제목·장군 마커, WAV 159개
- V173~V188 focused regressions
- V200 enemy CPU native commander-scan RED/GREEN Chromium regression
- V199 friendly CPU native action-word RED/GREEN Chromium regression
- V198 exact-zero retaliation RED/GREEN Chromium regression
- V197 native merge commander-bit RED/GREEN Chromium regression
- V196 dying occupied-slot contact RED/GREEN Chromium regression
- V195 native commander-bit combat RED/GREEN Chromium regression
- V194 killer-faction combat death-SFX RED/GREEN Chromium regression
- V193 native action-word combat gate RED/GREEN Chromium regression
- V192 lethal-hit retaliation/return-code RED/GREEN Chromium regression
- V191 strict bounded reach RED/GREEN Chromium regression
- V189 목표측 route tie backtrack Node/Chromium regression
- V190 승강기 경로·플랫폼·실제 탑승 Chromium regression
- V188 same-pass 울타리 종료 Chromium regression
- V187 자기 기지 제외 Chromium regression
- V199→V200 역패치 전체 바이트 동일성
- STAGES/SOUND_DATA 및 Base64 23개 동일
- 75개 스테이지 × 10 simulation pass invariant smoke
- JavaScript syntax 및 배포 archive identity

테스트된 V200 LITE Git blob: `cafe7c50af3954003072c54a1bb1eb42f7f706a9`.

## 이전 수정

- V200: CPU 적 장군 표적 스캔에서 성 HP/type 라벨 보정을 제거하고 원본 0x0800 비트만 사용.
- V199: CPU 아군 합류 후보의 행동 2/16 판정을 원본 packed action word low byte에서 읽도록 복원.
- V198: 반격 계산값이 정확히 0일 때 원본처럼 0 피해를 유지.
- V197: 아군 병합의 장군 판정을 원본 action word 0x0800 비트만 사용하도록 복원.
- V196: 사망 애니메이션 중 점유 슬롯을 원본처럼 접촉 차단 상태로 유지.
- V195: 장군 고정 피해 판정을 원본 action word의 0x0800 비트만 사용하도록 복원.
- V194: 전투 사망 효과음을 원본처럼 치명타를 가한 세력에서 선택.
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
