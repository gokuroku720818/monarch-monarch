# 모나크모나크 — V184 원본 패리티 복원판

원작 Windows 실행 파일·데이터·맵·효과음과 대조하며 개발 중인 비공식 HTML 복원판입니다. **V184도 아직 원작 전체의 장시간 동적 1:1 동일성을 주장하지 않습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V184 LITE 웹 기본판.
- `monarch_v184_lite.html`: 배포본과 바이트 동일한 V184 보관본.
- 원본 맵 75개와 WAV 효과음 159개 원본 바이트 검증을 유지합니다.
- BGM 포함 FULL HTML은 저장소에 커밋하지 않고 별도 완성 ZIP에 포함합니다.

## V184: 원본 패리티 체계 + 정확한 울타리 파괴 높이

원본 M_032의 (7,13) 열에는 z=3과 z=38에 울타리 코어가 동시에 존재합니다. V183은 높은 울타리 파괴 완료 뒤 같은 x/y 열을 재검색해 낮은 z=3 울타리로 목표를 바꿀 수 있었습니다.

V184는 원본 `lm_win.exe` Action 10의 저장 target x/y/z 사용 흐름에 맞춰, **명령 발행 시 정규화된 정확한 z를 실행 중 계속 유지**합니다. 선택한 구조물이 사라지면 명령을 끝내며 같은 열의 다른 높이 구조물로 자동 변경하지 않습니다.

M_032 실제 맵 Chromium 회귀에서 V183의 `z=38 → z=3` 재타깃을 실패 상태로 재현했고, V184는 높은 울타리만 제거한 뒤 Action 10을 종료하며 낮은 울타리를 그대로 보존합니다.

## 원본 패리티 하네스

V184부터 `parity/original-parity.json`으로 복원 규칙을 관리합니다.

- `CONFIRMED`: 원본 근거와 테스트가 연결된 규칙
- `PARTIAL`: 일부만 확인
- `UNKNOWN`: 근거 부족
- `BROWSER_ADAPTATION`: 모바일 터치 등 원작이라고 주장하지 않는 브라우저 적응

`tools/audit_parity.py`는 CONFIRMED 규칙의 구현 심볼·근거·테스트 경로가 실제 배포본/저장소에 존재하는지 검사합니다.

설계: [Original-Parity Restoration Design](docs/superpowers/specs/2026-09-28-monarch-original-parity-design.md)

V184 보고서: [V184_ORIGINAL_COMPARISON_REPORT.md](V184_ORIGINAL_COMPARISON_REPORT.md)

## V184 검증 범위

GitHub Actions run `36332529512`에서 다음 게이트가 모두 통과했습니다.

- 원본 75 MAP, 제목·장군 마커, WAV 159개
- V173~V183 focused regressions
- V184 M_032 exact-z Node/Chromium regression
- V183→V184 역패치 전체 바이트 동일성
- STAGES/SOUND_DATA 및 Base64 23개 동일
- 75개 스테이지 × 10 simulation pass invariant smoke
- JavaScript syntax 및 배포 archive identity

테스트된 V184 LITE Git blob: `78ace5e2a00d34510dba3a0606a0fcd8aa022cca`.

## 이전 수정

- V183: DF100 완성 다리의 무효 수리 명령 차단.
- V182: 울타리 작업 가능 조건과 명령 활성화 조건 일치.
- V181: 파괴/작업 명령의 지형 높이와 실제 작업 위치 일치.
- V180: 명령 중 시뮬레이션 일시정지.
- V179: 울타리 건설 위치 선택.
- V178: 높은 지형의 다리 상판 높이 판정.

## 아직 남은 원작 대조

이동/길찾기, 전투, 생산·세금·경제, CPU AI, 중립 AI, 난수·타이밍, 승패·점수, 원본 Windows UI/입력을 영역별로 계속 원본 EXE와 대조합니다. Windows 원본 실행파일을 같은 입력으로 자동 재생하는 동적 비교환경은 별도 런타임 랩 계획으로 관리합니다.
