# 모나크모나크 HTML 복원 프로젝트 — V171

원작을 대조하며 개발 중인 비공식 HTML 복원판입니다. 원작과 1:1 동일하다고 검증된 버전은 아닙니다.

## 현재 업로드 상태

README와 원작 비교 보고서는 업로드되어 있습니다. **게임 본편은 아직 GitHub에 업로드되지 않았습니다.** 대화에서 제공한 `monarch-v171-github-upload.zip`을 다운로드하고 압축을 풀어 아래 3개 파일을 저장소 루트에 올려야 플레이할 수 있습니다.

- `index.html` — 전체판 HTML (음악 스크립트를 외부 파일로 분리한 GitHub Pages 버전).
- `monarch-original-midi.js` — 전체판에 필수인 배경음악 데이터·재생 스크립트. 반드시 `index.html`과 같은 폴더에 둡니다.
- `monarch_v171_lite.html` — 배경음악 제외 경량판. 단독으로 열 수 있습니다.

`V171_ORIGINAL_COMPARISON_REPORT.md`는 이미 업로드했으므로 다시 올릴 필요가 없습니다.

## GitHub Pages

게임 파일을 `main` 브랜치 루트에 업로드한 뒤 Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/(root)` → Save. 실제 게시 여부는 Pages 설정에서 확인하세요.

## 전체판 분리 이유

원래 단일 HTML(약 26.3MB)은 GitHub 웹 업로드 파일 제한을 넘을 수 있어, 기존 게임·UI 스크립트는 변경하지 않고 마지막 MIDI 스크립트만 약 19.9MB의 별도 JS로 분리했습니다. 두 파일을 같은 디렉터리에 두면 원래 스크립트의 로딩 순서를 유지합니다. 전체 브라우저 동작에 대한 독립적인 장시간 검증까지 끝났다는 뜻은 아닙니다.

## 유의

원작 자산과 음악의 권리는 각 권리자에게 있습니다. 공식 배포판이 아니며 공개 배포 권한은 별도 확인이 필요합니다.
