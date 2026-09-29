# 모나크모나크 — V187 원본 패리티 복원판

원작 Windows 실행 파일·데이터·맵·효과음과 대조하며 개발 중인 비공식 HTML 복원판입니다. **V187도 아직 원작 전체의 장시간 동적 1:1 동일성을 주장하지 않습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V187 LITE 웹 기본판.
- `monarch_v187_lite.html`: 배포본과 바이트 동일한 V187 보관본.
- 원본 맵 75개와 WAV 효과음 159개 원본 바이트 검증을 유지합니다.
- BGM 포함 FULL HTML은 저장소에 커밋하지 않고 별도 완성 ZIP에 포함합니다.

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

## V187 검증 범위

GitHub Actions run `36502008881`에서 다음 게이트가 모두 통과했습니다.

- 원본 75 MAP, 제목·장군 마커, WAV 159개
- V173~V186 focused regressions
- V187 자기 기지 제외 Node/Chromium regression
- V186→V187 역패치 전체 바이트 동일성
- STAGES/SOUND_DATA 및 Base64 23개 동일
- 75개 스테이지 × 10 simulation pass invariant smoke
- JavaScript syntax 및 배포 archive identity

테스트된 V187 LITE Git blob: `2e91307fbff652dcd1b2010691c7441e335b35ab`.

## 이전 수정

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

이동/길찾기, 전투, 생산·세금·경제, CPU AI, 중립 AI, 난수·타이밍, 승패·점수, 원본 Windows UI/입력을 영역별로 계속 원본 EXE와 대조합니다. 비용이 드는 외부 서버는 사용하지 않고, 원본 EXE 정적 분석 + 원본 데이터 + Chromium + GitHub Actions로 계속 복원합니다.
