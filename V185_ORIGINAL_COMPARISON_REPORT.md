# 모나크모나크 V185 — 연속 생산기지 건설의 마지막 병력 1 복원

## 기준

- V184 LITE Git blob: `78ace5e2a00d34510dba3a0606a0fcd8aa022cca`.
- V184 FULL Git blob: `957a10266f4d4aeee5ab8c486b977ea1058053d1`.
- 이번 변경은 `repeatCandidateFromStand()`의 연속 생산기지 목표 탐색에서 병력 하한 한 곳과 버전 표기만 변경한다.
- MAP/STAGES, SOUND_DATA, 이미지·음성·음악 Base64, 전투·세금·AI 수치는 변경하지 않는다.

## V184에서 확인한 차이

실제 생산기지 작업 `tryBuildBase()`는 원본 `lm_win.exe 0x4333ac..0x433405`에 맞춰 병력 200 미만이면 절반을 작업량으로 쓰고, 계산값이 0이면 1로 보정한다. 따라서 병력 1인 부대도 마지막 1을 기지 건설에 쓸 수 있다.

그런데 V184의 연속작업 후보 탐색 `repeatCandidateFromStand()`는 `u.strength<=1`이면 다음 기지 목표를 찾지 않았다. 병력 2로 첫 기지를 짓고 병력 1이 된 계속건설 부대가 원작 작업기가 허용하는 마지막 건설 기회를 한 번 일찍 잃는 차이다.

## 원본 EXE 근거

- `0x43b901..0x43b930`: 작업 반환값이 `0x400`이면 계속작업 경로로 들어가 생산기지용 반복 탐색 wrapper `0x43e8bb`를 호출.
- `0x43e8bb..0x43e90e`: action 4 반복 탐색을 `0x43eb4c`로 넘기며 병력(+0x4)을 검사하지 않음.
- `0x43eb4c..0x43ec91`: 일반 반복작업 탐색은 유닛 target/state를 갱신하지만 병력 필드(+0x4)를 읽지 않음. action 4는 유일한 추가 `0x43fb9b` 검증 case에도 들어가지 않음.
- `0x4333ac..0x433405`: 실제 생산기지 건설은 계산 작업량이 0이면 1로 보정해 마지막 병력 1을 소비할 수 있음.

## V185 수정

기능 변경은 한 조건뿐이다.

- V184: `strength<=1`이면 다음 생산기지 목표 탐색 중단.
- V185: `strength<=0`일 때만 중단.

자금 조건, 지형 조건, 인접 높이, 근처 자국 기지 검사, 실제 건설비 100, 건설 작업량 및 사망 처리는 그대로 유지한다.

## 실패 우선 검증

새 Node 회귀:

- 병력 1 + 자금 100 + 인접 유효 건설 지형 → 다음 Action 4 후보가 있어야 함.
- 병력 0 → 후보 없음.
- 병력 1 + 자금 99 → 기존 자금 gate 유지, 후보 없음.

V184는 첫 조건에서 `actual null`로 실패했고 V185 LITE/FULL은 모두 통과했다.

## Chromium 검증

실제 배포 엔진을 로드하고 5×5의 격리 건설 가능 지형에서 병력 1인 계속건설 부대를 시험했다.

V185 LITE/FULL 모두:

- 다음 생산기지 후보 발견
- `assignNextManualWork() === true`
- `actionCode === 4`
- `actionTarget` 설정
- runtime/page error 0

FULL 브라우저 검증은 대용량 내장 MIDI playback script만 테스트 하네스에서 제거하고 동일 게임 엔진을 실행했다.

## 자산 및 안정성

- V185 조건과 버전 표기만 역변환하면 V184 HTML과 전체 바이트 동일.
- STAGES 동일.
- SOUND_DATA 동일.
- 내장 Base64 payload 23개 동일.
- V185 LITE 75개 스테이지 × 각 10 simulation pass: 75/75 완료, invariant/runtime/page error 0.

## GitHub Actions

- workflow run `36434397405`: **success**.
- exact V184 blob 생성, manifest/audit, 원본 75 MAP·제목/장군·WAV 159개, V173~V184 focused regressions, 새 V185 Node/Chromium 회귀, 자산 안정성, 75-stage invariant, JS syntax가 모두 success.
- bot staging commit: `ef7556877e34fff777ff4170d3b831a1c87ff0c7`.
- staging `index.html`과 `monarch_v185_lite.html` Git blob은 모두 `5d68d7a76e4ffe6250f24c776f5a9b81722dcf66`로 로컬 검증 LITE와 동일.

## 생성 결과

- V185 LITE Git blob: `5d68d7a76e4ffe6250f24c776f5a9b81722dcf66`.
- V185 LITE SHA-256: `dbe9865f69bdc5fd221a77f418f3ceb62573e6c46ec23bce1c9fe91387161166`.
- V185 FULL Git blob: `5ae3bd04d493329d9214bf993330929d69503bd3`.
- V185 FULL SHA-256: `46a5198df589c176f21cd6c50a8c75d94386b24b8db9f6ba488c8c5ca2ed64f8`.

## 한계

원본 Windows 실행파일을 직접 실행해 동일 입력을 자동 재생하는 동적 비교는 하지 못했다. 비용이 드는 DigitalOcean은 사용하지 않으며, V185 근거는 사용자 제공 원본 EXE 정적 분석, 원본 데이터, 실패 우선 회귀 및 Chromium 실행에 한정한다.
