# 모나크모나크 — V183 HTML 복원판

원작 Windows 실행 파일·맵·효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **원작 AI·전투·경제·승패를 포함한 장시간 1:1 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V183 LITE 웹 기본판. 원본 맵 75개, 스프라이트, WAV 효과음 159개 포함. BGM 제외.
- `monarch_v183_lite.html`: `index.html`과 바이트 동일한 V183 보관본.
- `monarch_v182_lite.html` 및 이전 파일: 이전 버전 별도 보관.
- BGM 13곡을 포함한 전체 HTML과 ZIP은 ChatGPT 대화에서 별도로 제공합니다.

## V183: 완성된 다리에 내려지던 무효 수리 명령 차단

V182의 명령 메뉴는 DF100 완성 다리에서 다리 건설/수리 버튼을 비활성화했고 실제 `workBridge()`도 작업을 거절했지만, 직접 명령 발행 경로인 `issueBridge()`는 완성 다리를 받아들이는 불일치가 있었습니다. V183은 `bridgeOrderStand()`에서도 동일한 DF 판정을 수행하여 DF100 완성 다리는 명령 발행 단계에서 거부하고 기존 병사 명령을 보존합니다.

DF100 미만 완성 다리, 손상 다리, 공사 발판, 물 위 신규 다리는 기존 동작을 유지합니다. V182에서 실패하는 회귀 테스트를 먼저 확인한 뒤 V183 경량판·전체판에서 통과시켰고, 실제 Chromium에서도 DF100 거부와 DF70 수리 허용을 확인했습니다. GitHub Actions에서 원본 자원 검사와 기존 울타리·다리·작업 높이·명령 일시정지·장군 패배·병력 슬롯·터치 포커스 회귀 및 JavaScript 문법 검사까지 통과했습니다. 자세한 범위는 [V183 비교 보고서](V183_ORIGINAL_COMPARISON_REPORT.md)를 참조하십시오.

## 이전 수정

- V182: 완성·고립·공간 부족·높이 초과 울타리의 실행 불가능 명령 차단. [V182 보고서](V182_ORIGINAL_COMPARISON_REPORT.md)
- V181: 나무·식생 제거, 기지·다리·울타리 파괴, 구덩이 봉쇄 명령 위치의 작업 높이 정렬. [V181 보고서](V181_ORIGINAL_COMPARISON_REPORT.md)
- V180: 부대·장군 명령 중 시뮬레이션 일시정지 및 명령 종료 후 재개. 원작 Windows EXE의 일시정지 여부는 직접 대조하지 못했습니다. [V180 보고서](V180_ORIGINAL_COMPARISON_REPORT.md)
- V179: 울타리 건설 가능한 위치 선택. [V179 보고서](V179_ORIGINAL_COMPARISON_REPORT.md)
- V178: 높은 둑의 다리 건설 높이 판정. [V178 보고서](V178_ORIGINAL_COMPARISON_REPORT.md)
- V177: 장군 패배 후 오래된 명령창 정리. V176: 부대 슬롯 재사용 명령 메뉴 정리. V175: 모바일 포커스. V174: 터치 드래그. V173: 효과음 이름 대소문자 처리.

## 회귀 검사

`python3 tests/test_original_parity.py index.html`: 원본 맵·스테이지 제목·장군 마커·WAV 효과음.

`node tests/test_bridge_command_validity.js index.html`: 완성 다리 거부 및 손상 다리/신규 건설 유지.

`node tests/test_fence_command_validity.js index.html`, `node tests/test_work_height.js index.html`, `node tests/test_command_pause.js index.html`, `node tests/test_bridge_deck_height.js index.html`, `node tests/test_fence_order_height.js index.html`: 기존 기능 검사. 장군 패배·병력 슬롯 재사용·터치 포커스 및 JS 문법도 GitHub Actions에서 검증합니다. `scripts/upgrade_v183.py`는 **정확한 V182 Git blob에서만** 새 버전을 생성합니다.

## 남은 원작 대조

Windows EXE와 HTML에서 동일 명령으로 장시간 플레이하며 AI·경제·전투·승패를 비교하는 검증은 아직 완료되지 않았습니다. V183은 확인된 다리 명령 불일치를 수정한 단계이지 원작 전체와 동일하다는 뜻은 아닙니다.
