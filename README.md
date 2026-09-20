# 모나크모나크 — V173 HTML 복원판

원작 Windows 실행 파일/맵/효과음과 비교하며 개발 중인 비공식 HTML 복원판입니다. **장시간 게임 AI·전투·경제를 포함한 완전한 원작 동일성은 아직 검증되지 않았습니다.** 원작 소프트웨어 및 음악·자산의 권리는 각각의 권리자에게 있습니다.

## 게임 실행

**GitHub Pages:** https://gokuroku720818.github.io/monarch-monarch/

- `index.html` — V173 LITE 웹사이트 기본 실행 파일. 75맵·스프라이트·원본 WAV 159개를 포함하고 배경음악은 포함하지 않습니다.
- `monarch_v173_lite.html` — `index.html`과 바이트가 동일한 버전별 보관본.
- `monarch_v172_lite.html` — 이전 버전 보관본으로 변경하지 않았습니다.

## V173에서 고친 원본 호환성

Windows 원본은 WAV 파일명을 대소문자 구별 없이 찾지만 이전 HTML은 `SOUND_DATA[name]`만 사용했습니다. 원본에 존재하는 `lm0200.wav`를 `LM0200.WAV`로 요청하거나 `LM0000.WAV`를 `lm0000.wav`로 요청하면 재생하지 못했습니다. V173에서는 원래 이름 → 소문자 이름 → 대문자 이름으로 조회해 수정했습니다. 게임 로직/AI/경제·맵·원본 오디오 바이트는 변경하지 않았습니다.

## 원작 데이터 회귀 검사

`python3 tests/test_original_parity.py index.html`을 실행하면 Windows 원본에서 확인한 기준 SHA-256을 이용해 75개 맵 격자/실제 제목·장군 마커 및 159개 WAV 오디오 바이트가 보존됐는지 확인할 수 있습니다. `scripts/upgrade_v173.py`와 `.github/workflows/upgrade-v173.yml`은 기존 HTML Git Blob을 확인하고 원본 데이터 검사를 통과한 경우에만 V173을 배포합니다. 세부 내용은 `V173_ORIGINAL_COMPARISON_REPORT.md` 참고.

## 배경음악과 남은 검증

GitHub의 V173 LITE에는 원작 배경음악 13곡이 없습니다. 전체 BGM 포함 V173 단일 HTML/ZIP은 별도로 제공됩니다. 원본 EXE와 HTML의 장시간 AI/명령/전투 결과를 1:1로 대조하는 검증은 남아 있습니다.
