# 모나크모나크 — V176 HTML 복원판

원작 Windows 실행 파일·맵·효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **장시간 AI·전투·경제·승패를 포함한 원작 완전 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어 및 음악·자산의 권리는 각각의 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html` — V176 LITE 웹사이트 기본 실행 파일. 원본 75개 맵·스프라이트·WAV 효과음 159개를 포함하며 배경음악은 포함하지 않습니다.
- `monarch_v176_lite.html` — `index.html`과 동일한 V176 보관본.
- `monarch_v175_lite.html` 및 이전 버전 — 수정하지 않은 보관본.

## V176에서 수정한 부대 슬롯 재사용 오류

선택한 병사가 사라지고 같은 원작 64슬롯 번호에 새 병사가 생성되면, V175에서는 선택 목록이 비어도 이전 병사의 명령 메뉴와 목적지가 남았습니다. V176은 슬롯 재사용 시 UI 정리를 강제로 요청해 오래된 명령 메뉴를 닫고 선택 단계로 돌아갑니다. 64슬롯 할당, 부대 생산·이동·전투·AI·경제·맵·원본 음향은 변경하지 않았습니다.

## 이전 변경점

V175: 화면 포커스 손실 뒤 남는 터치 식별자 초기화. V174: 모바일 드래그를 기존 마우스 사각형 선택에 연결. V173: 원본 WAV 파일명 대소문자 비구분 검색 복원.

## 원작 자산 및 회귀 검사

`python3 tests/test_original_parity.py index.html`은 원본에서 확인한 SHA-256 기준으로 맵 75개(지형·제목·장군 위치), WAV 159개의 보존을 확인합니다. `node tests/test_recycled_slot_cleanup.js index.html`은 실제 배포 UI 정리 함수를 실행하여 이번 회귀 오류를 점검합니다. `node tests/test_touch_focus_adapter.js index.html`은 터치 처리 재발 오류를 검사합니다. `scripts/upgrade_v176.py`와 `.github/workflows/upgrade-v176.yml`은 정확한 V175 Git Blob에서만 V176을 생성하고 검사 통과 후 커밋합니다. 근거: `V176_ORIGINAL_COMPARISON_REPORT.md`.

## 남은 검증

GitHub Pages는 원본 배경음악이 빠진 경량판입니다. BGM 포함 전체 HTML/ZIP은 대화에서 별도로 제공됩니다. 원본 Windows 실행 파일과 HTML의 장시간 AI·전투·경제·승패 결과를 동일 명령으로 1:1 검증하는 작업은 남아 있습니다.
