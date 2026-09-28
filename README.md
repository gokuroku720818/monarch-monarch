# 모나크모나크 — V186 원본 패리티 복원판

원작 Windows 실행 파일·데이터·맵·효과음과 대조하며 개발 중인 비공식 HTML 복원판입니다. **V186도 아직 원작 전체의 장시간 동적 1:1 동일성을 주장하지 않습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V186 LITE 웹 기본판.
- `monarch_v186_lite.html`: 배포본과 바이트 동일한 V186 보관본.
- 원본 맵 75개와 WAV 효과음 159개 원본 바이트 검증을 유지합니다.
- BGM 포함 FULL HTML은 저장소에 커밋하지 않고 별도 완성 ZIP에 포함합니다.

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

## V186 검증 범위

GitHub Actions run `36436360034`에서 다음 게이트가 모두 통과했습니다.

- 원본 75 MAP, 제목·장군 마커, WAV 159개
- V173~V185 focused regressions
- V186 자금부족 대기 Node/Chromium regression
- V185→V186 역패치 전체 바이트 동일성
- STAGES/SOUND_DATA 및 Base64 23개 동일
- 75개 스테이지 × 10 simulation pass invariant smoke
- JavaScript syntax 및 배포 archive identity

테스트된 V186 LITE Git blob: `7f26de67871cbd547c853b371e0e041a3fb92b61`.

## 이전 수정

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
