# 모나크모나크 — V175 HTML 복원판

원작 Windows 실행 파일·맵·효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **장시간 AI·전투·경제·승패를 포함한 원작 완전 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어 및 음악·자산의 권리는 각각의 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html` — V175 LITE 웹사이트 기본 실행 파일. 원본 75개 맵·스프라이트·WAV 효과음 159개를 포함하며 배경음악은 포함하지 않습니다.
- `monarch_v175_lite.html` — `index.html`과 동일한 V175 보관본.
- `monarch_v174_lite.html` 및 이전 버전 — 수정하지 않은 보관본.

## V175에서 수정한 입력 오류

모바일 터치 드래그 도중 앱·탭이 백그라운드로 이동하여 `blur`가 발생하고 `touchend`가 누락되면, V174는 손가락 식별자가 남아 다음 드래그를 무시하는 문제가 있었습니다. V175는 포커스를 잃을 때 이 식별자를 초기화합니다. 기존 원작 기반 PC 선택 처리, 이동·전투·AI·경제·맵·효과음 바이트는 변경하지 않았습니다.

## 이전 V174 및 V173 변경점

V174: 휴대폰 한 손가락 드래그를 기존 마우스 사각형 선택 처리에 연결했습니다. V173: Windows 원본 WAV 파일명의 대소문자 비구분 검색을 복원했습니다.

## 원작 자산 및 회귀 검사

`python3 tests/test_original_parity.py index.html`은 원본에서 확인한 고정 SHA-256 기준으로 맵 75개(지형·제목·장군 위치), WAV 159개 데이터의 보존을 확인합니다. `node tests/test_touch_focus_adapter.js index.html`은 배포된 HTML의 터치 처리 코드를 실제로 실행하여 포커스 복귀 입력 오류를 검사합니다. `scripts/upgrade_v175.py`와 `.github/workflows/upgrade-v175.yml`은 정확한 V174 Git Blob에서만 V175를 생성하고 검사를 통과한 경우에만 커밋합니다. 상세 근거: `V175_ORIGINAL_COMPARISON_REPORT.md`.

## 남은 검증

GitHub Pages는 원본 배경음악이 빠진 경량판입니다. BGM 포함 전체 HTML/ZIP은 대화에서 별도로 제공됩니다. 원본 Windows 실행 파일과 HTML의 장시간 AI·전투·경제·승패 결과를 동일 명령으로 1:1 검증하는 작업은 남아 있습니다.
