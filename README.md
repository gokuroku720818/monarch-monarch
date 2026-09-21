# 모나크모나크 — V181 HTML 복원판

원작 Windows 실행 파일·맵·효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **원작 AI·전투·경제·승패를 포함한 장시간 1:1 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어와 자산의 권리는 각 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html`: V181 LITE 웹 기본판. 원본 맵 75개, 스프라이트, WAV 효과음 159개 포함. BGM 제외.
- `monarch_v181_lite.html`: `index.html`과 바이트 동일한 V181 보관본.
- `monarch_v180_lite.html` 및 이전 파일: 이전 버전 별도 보관.
- BGM 13곡을 포함한 전체 HTML과 ZIP은 ChatGPT 대화에서 별도로 제공합니다.

## V181: 제거·파괴·봉쇄 명령이 작업 불가능한 지형을 선택하는 오류

V180에서는 나무 제거·식생 제거·생산기지 파괴·다리 파괴·울타리 파괴·구덩이 봉쇄 명령이 길찾기만 확인해, 실제 작업 사거리 밖의 높은 둑을 작업 위치로 선택했습니다. 실제 행동 분기의 `originalActionAdjacent()`는 동서남북 한 칸과 높이 차이 -2~+3을 요구합니다. V181은 명령 메뉴와 위치 선택 양쪽에 이 조건을 적용하고, 울타리 상단 클릭 시 실제 하단 코어 높이를 사용합니다. 전부 불가능하면 명령을 거부하고 기존 병사 명령을 유지합니다.

V180에서 실패하는 실제 코드 기반 테스트를 만든 다음 V181에서 7가지 유형의 유효/불가 작업 위치를 검증했습니다. 경량판과 BGM 포함 전체판 각각 75개 맵×100틱 Chromium 검사, 기존 명령 일시정지·다리·울타리 회귀 테스트, 원본 맵 75개·효과음 159개·내장 자산 보존 검사를 통과했습니다. 자세한 근거와 미검증 범위는 [V181 보고서](V181_ORIGINAL_COMPARISON_REPORT.md)에 기록했습니다.

## 이전 수정

- V180: 부대·장군 명령 중 시뮬레이션 일시정지, 확정·취소 후 재개, 사용자 수동 정지 유지. 원작 Windows EXE의 명령 일시정지 여부는 직접 대조하지 못했습니다. [V180 보고서](V180_ORIGINAL_COMPARISON_REPORT.md)
- V179: 울타리 건설 가능한 위치 선택. [V179 보고서](V179_ORIGINAL_COMPARISON_REPORT.md)
- V178: 높은 둑의 다리 건설 높이 판정. [V178 보고서](V178_ORIGINAL_COMPARISON_REPORT.md)
- V177: 장군 패배 후 오래된 명령창 정리. V176: 부대 슬롯 재사용 명령 메뉴 정리. V175: 모바일 포커스. V174: 터치 드래그. V173: 효과음 이름 대소문자 처리.

## 회귀 검사

`python3 tests/test_original_parity.py index.html`: 원본 맵·스테이지 제목·장군 마커·WAV 효과음.

`node tests/test_work_height.js index.html`: 실제 제거·파괴·봉쇄 명령의 작업 위치 높이 검사.

`node tests/test_command_pause.js index.html`, `node tests/test_bridge_deck_height.js index.html`, `node tests/test_fence_order_height.js index.html`: 기존 기능 검사. 장군 패배·병력 슬롯 재사용·터치 포커스 및 모든 JavaScript 문법 검사도 GitHub Actions에서 실행합니다. `scripts/upgrade_v181.py`는 **정확한 V180 Git blob에서만** 다음 버전을 생성합니다.

## 남은 원작 대조

Windows EXE와 HTML에서 동일 명령으로 장시간 플레이하며 AI·경제·전투·승패를 비교하는 검증은 아직 끝나지 않았습니다. V181은 확인된 작업 위치 오류를 수정한 단계이지 원작 전체와 동일하다는 뜻은 아닙니다.
