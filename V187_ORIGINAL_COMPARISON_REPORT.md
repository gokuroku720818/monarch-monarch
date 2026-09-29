# 모나크모나크 V187 — 연속 생산기지 파괴에서 자기 기지 제외

## 기준

- V186 LITE Git blob: `7f26de67871cbd547c853b371e0e041a3fb92b61`.
- V186 FULL Git blob: `b46bc545b6f4d5bfb5534f7a8213891ae8daa858`.
- V187 기능 변경은 `repeatCandidateFromStand(..., 'destroyBase', ...)`의 Action 8 반복 후보에서 **자기 진영 생산기지 타일 `29+faction`을 제외**하는 한 지점으로 한정한다.

## V186에서 재현한 차이

V186의 연속 생산기지 파괴 탐색은 타일 29..32를 모두 Action 8 후보로 받아들였다. 따라서 적 기지를 하나 파괴한 뒤 계속작업 탐색이 자기 진영 기지를 만나면 자기 기지를 다음 파괴 목표로 선택할 수 있었다.

실패 우선 Node 회귀에서 faction 0 병사 옆에 자기 기지 tile 29만 둔 경우 V186은 기대값 `null` 대신 실제 Action 8 후보를 반환했다.

## 원본 EXE 근거

- `lm_win.exe 0x43e90f..0x43e96a`: Action 8 반복작업 wrapper가 후보 테이블을 초기화한 뒤 타일 29..32 네 개를 활성화한다.
- 같은 wrapper에서 현재 faction 값을 인덱스로 `0x4ca275 + faction`의 bit 0을 다시 지운다. `0x4ca275`는 후보 테이블에서 tile 29 위치이므로 결과적으로 `29+faction` 자기 생산기지만 제외된다.
- 이후 wrapper는 action 8을 인수로 범용 반복 탐색기 `0x43eb4c`를 호출한다.
- `0x43eb4c..0x43ec91`은 남은 후보 중 도달 가능한 셀을 찾으면 해당 target과 action 8을 현재 유닛에 기록한다.

따라서 원본의 계속 파괴는 적 생산기지는 대상으로 유지하지만 자기 생산기지는 후보에서 제외한다.

## V187 수정

기존:

`if(t>=29&&t<=32)`

V187:

`if(t>=29&&t<=32&&t!==29+u.f)`

그 외 반복탐색 BFS, 경로, 파괴력, 생산기지 내구도/소유권, 경제, 전투, AI, 자산은 변경하지 않았다.

## 검증

- V186 RED: 자기 기지 tile 29를 Action 8 반복 후보로 잘못 반환.
- V187 LITE/FULL Node GREEN: faction 0의 tile 29, faction 3의 tile 32는 제외하고 적 기지는 유지.
- Chromium 실제 엔진: 서쪽(탐색 우선)의 자기 기지 tile 29를 건너뛰고 동쪽 적 기지 tile 30을 Action 8 target으로 선택. LITE/FULL 모두 runtime/page error 0.
- V186→V187 패치와 버전 표기만 역변환하면 전체 HTML이 V186과 바이트 동일.
- STAGES 동일, SOUND_DATA 동일, 내장 Base64 payload 23개 동일.
- V187 LITE 75개 스테이지 × 각 10 simulation pass: 75/75, invariant/runtime/page error 0.

## 생성 결과

- V187 LITE Git blob: `2e91307fbff652dcd1b2010691c7441e335b35ab`.
- V187 LITE SHA-256: `6fcb463ef5d37ca186e2775a7685c47fcac0321f5d734a8e7146374f283e39c7`.
- V187 FULL Git blob: `b9b856a83bc07aa62d57d6d636b00568cdc707f7`.
- V187 FULL SHA-256: `b5fa6bee554669eb0dd0b5e4f35fac9a58557ea9813828cd8ef9fe2bd68b89c5`.
- V187 complete ZIP SHA-256: `1f756cf9aa226fcda1d3b8ab2b235b0c97d1f64f5d3e4d0e9437f8d1625cd53d`.

## GitHub Actions 검증

- workflow run `36502008881`: **success**.
- exact V186 blob 생성, 패리티 manifest/audit, 원본 75 MAP·제목/장군·WAV 159개, V173~V186 focused regressions, V187 Node/Chromium 회귀, 자산 안정성, 75-stage invariant, JS syntax 모두 success.
- CI staging commit: `88f944070684132c1de693892657d4c3d169989a`.
- staging `index.html`과 `monarch_v187_lite.html` Git blob은 모두 `2e91307fbff652dcd1b2010691c7441e335b35ab`로 로컬 검증 LITE와 일치한다.

## 한계

원본 Windows 실행파일의 동적 캡처는 하지 않았다. 비용이 드는 외부 서버는 사용하지 않으며, 원본 EXE 정적 제어흐름 + 원본 데이터 + 실패 우선 회귀 + Chromium + GitHub Actions를 근거로 복원한다.
