# 모나크모나크 — V172 HTML 복원판

원작 규칙과 자산을 비교하며 개발 중인 비공식 복원판입니다. 전체 게임의 원작 동일성은 아직 검증되지 않았습니다.

## GitHub에 업로드된 실행 파일

- **`index.html`** — V172 경량판 기본 진입점. 스프라이트·75맵·원본 WAV 효과음을 포함합니다. 저장소에 없는 배경음악 JS를 불러오지 않으므로 파일 단독 실행이 가능합니다.
- **`monarch_v172_lite.html`** — 위 `index.html`과 바이트 동일한 보관본.
- **`scripts/upgrade_v172.py`**, **`.github/workflows/upgrade-v172.yml`** — V171 게임 HTML의 미디어 데이터를 변조하지 않고 UI 버그를 수정한 생성 코드와 배포 워크플로.
- **`V172_ORIGINAL_COMPARISON_REPORT.md`** — 수정 및 검증 범위와 미완료 항목.

### 원작 배경음악

GitHub에는 원본 OGG/MIDI 재생용 `monarch-original-midi.js`가 **업로드되지 않았습니다.** 따라서 GitHub 실행판은 배경음악이 빠진 경량판입니다. ChatGPT 대화에서 별도로 제공한 V172 전체 HTML에는 기존 원본 13곡이 들어 있습니다. 원작 소프트웨어와 음악의 권리는 각각의 권리자에게 있습니다.

### GitHub Pages

공개 사이트를 이용하려면 Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/(root)`를 지정하세요. 실제 GitHub Pages 활성화와 URL 접속 여부는 별도로 확인해야 합니다.

### V172 변경점

드래그 선택이 발밑 좌표만 검사해 보이는 부대를 놓치던 문제를 32×48 스프라이트 영역과 드래그 사각형의 겹침 검사로 수정했습니다. 버전 배지와 제목 표시도 정정했습니다. 게임플레이 엔진, 75맵 음악 매핑 및 원본 스프라이트 데이터는 유지합니다.
