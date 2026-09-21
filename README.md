# 모나크모나크 — V182 HTML 복원판

원작 Windows 실행 파일·맵·효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **원작 AI·전투·경제·승패를 포함한 장시간 1:1 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V182 LITE 웹 기본판. 원본 맵 75개, 스프라이트, WAV 효과음 159개 포함. BGM 제외.
- `monarch_v182_lite.html`: `index.html`과 바이트 동일한 V182 보관본.
- `monarch_v181_lite.html` 및 이전 파일: 이전 버전 별도 보관.
- BGM 13곡을 포함한 전체 HTML과 ZIP은 ChatGPT 대화에서 별도로 제공합니다.

## V182: 실행할 수 없는 울타리 명령 차단

V181에서는 이미 내구도 DF200으로 완성된 울타리에 수리 명령을 내려도 작업 함수가 거부하여 병력이 의미 없는 명령을 유지할 수 있었습니다. 명령 메뉴에서는 두 층 공간이 막혔거나 건설 높이 상한을 벗어난 신규 울타리에도 건설 명령이 활성화됐습니다. V182는 메뉴와 실제 명령 함수 양쪽을 작업 엔진의 조건에 맞춰 정렬하여 완성·고립·공간 부족·높이 초과 대상을 거부하고, 손상된 울타리 수리 및 정상 신규 건설은 유지합니다.

V181에서 실패하는 테스트를 먼저 만든 후 V182에서 통과를 확인했습니다. 경량판과 전체판 실제 Chromium 게임 화면에서 완성 울타리의 명령 버튼 비활성화 → 손상된 울타리의 수리 활성화를 확인했습니다. 기존 다리·울타리·작업 높이·명령 일시정지 회귀 테스트, 원본 맵 75개와 WAV 159개 및 내장 자산 무변경 검사 통과. 각 75개 맵을 10틱씩 실행했으며 V182의 75맵×100틱 테스트는 시간 제한으로 완료하지 못했습니다. 자세한 범위는 [V182 비교 보고서](V182_ORIGINAL_COMPARISON_REPORT.md)를 참조하십시오.

## 이전 수정

- V181: 나무·식생 제거, 기지·다리·울타리 파괴, 구덩이 봉쇄 명령 위치의 작업 높이 정렬. [V181 보고서](V181_ORIGINAL_COMPARISON_REPORT.md)
- V180: 부대·장군 명령 중 시뮬레이션 일시정지 및 명령 종료 후 재개. 원작 Windows EXE의 일시정지 여부는 직접 대조하지 못했습니다. [V180 보고서](V180_ORIGINAL_COMPARISON_REPORT.md)
- V179: 울타리 건설 가능한 위치 선택. [V179 보고서](V179_ORIGINAL_COMPARISON_REPORT.md)
- V178: 높은 둑의 다리 건설 높이 판정. [V178 보고서](V178_ORIGINAL_COMPARISON_REPORT.md)
- V177: 장군 패배 후 오래된 명령창 정리. V176: 부대 슬롯 재사용 명령 메뉴 정리. V175: 모바일 포커스. V174: 터치 드래그. V173: 효과음 이름 대소문자 처리.

## 회귀 검사

`python3 tests/test_original_parity.py index.html`: 원본 맵·스테이지 제목·장군 마커·WAV 효과음.

`node tests/test_fence_command_validity.js index.html`: 신설/수리 가능 여부 및 기존 행동 보존.

`node tests/test_work_height.js index.html`, `node tests/test_command_pause.js index.html`, `node tests/test_bridge_deck_height.js index.html`, `node tests/test_fence_order_height.js index.html`: 기존 기능 검사. 장군 패배·병력 슬롯 재사용·터치 포커스 및 JS 문법도 GitHub Actions에서 검증합니다. `scripts/upgrade_v182.py`는 **정확한 V181 Git blob에서만** 새 버전을 생성합니다.

## 남은 원작 대조

Windows EXE와 HTML에서 동일 명령으로 장시간 플레이하며 AI·경제·전투·승패를 비교하는 검증은 아직 완료되지 않았습니다. V182는 확인된 울타리 명령 오류를 수정한 단계이지 원작 전체와 동일하다는 뜻은 아닙니다.
