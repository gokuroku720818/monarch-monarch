# 모나크모나크 V186 — 연속 생산기지의 자금부족 대기 동작 복원

## 기준

- V185 LITE Git blob: `5d68d7a76e4ffe6250f24c776f5a9b81722dcf66`.
- V185 FULL Git blob: `5ae3bd04d493329d9214bf993330929d69503bd3`.
- V186 기능 변경은 생산기지 연속작업에서 (1) 다음 목표 탐색의 자금 선검사를 제거하고, (2) 이미 Action 4 목표에 도착했을 때 자금 100 미만이면 Action 4를 끝내지 않고 유지하는 두 지점으로 한정한다.

## V185에서 확인한 차이

V185는 병력 1의 마지막 건설은 허용하도록 복원했지만, `repeatCandidateFromStand('base')`가 자금 100 미만이면 다음 생산기지 목표 자체를 선택하지 않았다. 또한 Action 4 실행 중 `tryBuildBase()`가 false를 반환하면 즉시 `finishWorkAction()`을 호출했다.

원본 EXE는 목표 선택과 실제 자금 차감을 분리한다.

## 원본 EXE 근거

- `0x43e8bb..0x43e90e`: 생산기지 계속작업 wrapper가 자금 검사를 하지 않고 action 4로 일반 반복 탐색기 `0x43eb4c`를 호출한다.
- `0x43eb4c..0x43ec91`: 반복 탐색기가 다음 목표를 선택·저장하며 faction treasury를 읽지 않는다.
- `0x4332cb..0x4332de`: 실제 기지 작업 위치에서만 100을 인수로 `0x430640`을 호출한다. 지불 실패면 worker return code 1로 종료한다.
- `0x430640..0x43069e`: 활성 faction 자금을 확인해 충분할 때만 차감하고 1을, 부족하면 0을 반환한다.
- `0x43b8df..0x43b8eb`: 기지 worker return 1은 `0x43bded`의 완료/계속 retarget 처리를 호출하지 않고 dispatcher 끝으로 빠진다. 즉 현재 Action 4가 유지되어 다음 pass에서 재시도된다.

따라서 원작은 자금이 100 미만이어도 계속건설 목표를 먼저 잡고, 작업 위치에서 자금이 생길 때까지 기다리는 흐름이다.

## 실패 우선 검증

V185에 새 회귀를 실행하면 자금 99, 병력 50, 인접 유효 지형에서 기대한 action 4 후보 대신 실제값 `null`로 실패했다.

V186에서는 자금 99에서도 다음 action 4 목표를 선택하고, 목표 위치에서는 build worker와 `finishWorkAction()`을 호출하지 않은 채 Action 4를 유지한다. 자금이 100이 되면 같은 목표를 실제 건설한다.

## 기존 V185 테스트 조정

V185의 `test_base_continue_last_strength.js`에는 당시 아직 원본 검증이 끝나지 않은 자금 동작을 보수적으로 고정한 `resource 99 -> null` assertion이 있었다. V186의 EXE 근거가 이 가정을 반박했기 때문에 이 assertion을 제거했다. 병력 1/0 경계 검증은 그대로 유지하며, 자금 동작은 V186 전용 `test_base_continue_funding_wait.js`가 담당한다.

## Chromium 검증

격리된 건설 가능 지형에서 병력 50, 자금 99인 계속건설 부대를 실제 V186 엔진으로 실행했다.

1. 다음 생산기지 목표를 정상 획득.
2. 자금 99 상태에서 simulation pass를 실행해도 Action 4와 동일 target, 병력 50, 자금 99, 미건설 상태 유지.
3. 자금을 100으로 올린 뒤 다음 pass에서 해당 셀에 생산기지 tile 29 건설.
4. 자금 0, 병력 25가 되고, 계속작업 규칙에 따라 다음 Action 4 목표를 다시 획득.
5. runtime/page error 0.

LITE/FULL 모두 통과했으며 FULL 브라우저 검증은 테스트 하네스에서 대용량 MIDI playback script만 제거하고 동일 게임 엔진을 실행했다.

## 자산 및 안정성

- V186의 두 코드 변화와 버전 표기만 역변환하면 V185 HTML과 전체 바이트 동일.
- STAGES 동일.
- SOUND_DATA 동일.
- 내장 Base64 payload 23개 동일.
- V186 LITE 75개 스테이지 × 각 10 simulation pass: 75/75 완료, invariant/runtime/page error 0.

## 생성 결과

- V186 LITE Git blob: `7f26de67871cbd547c853b371e0e041a3fb92b61`.
- V186 LITE SHA-256: `7aa9152793142651bbc08006a3e39a2c7d3f1caab2863b7594157420e8b467dc`.
- V186 FULL Git blob: `b46bc545b6f4d5bfb5534f7a8213891ae8daa858`.
- V186 FULL SHA-256: `981fdbf61d7ad5aa7b15c282f95698a38792857458c317639c8fface91686bb6`.
- V186 complete ZIP SHA-256: `7fe0067819321f044300832380fc20f2422c6c5098b093239f60d98c78e0e025`.

## GitHub Actions 검증

- 첫 run `36436149507`은 V185 회귀 테스트에 남아 있던 임시 `resource 99 -> null` 가정 때문에 실패했다.
- 수정 후 run `36436360034`: **success**.
- exact V185 blob 생성, parity manifest/audit, 원본 75 MAP·제목/장군·WAV 159개, V173~V185 focused regressions, V186 Node/Chromium 자금대기 회귀, 자산 안정성, 75-stage invariant, JS syntax 모두 success.
- CI staging commit: `3952c04b8b88fead7e172e517f65bd9d7e0cf7d7`.
- staging `index.html`과 `monarch_v186_lite.html` Git blob은 모두 `7f26de67871cbd547c853b371e0e041a3fb92b61`로 로컬 검증 LITE와 일치한다.

## 한계

원본 Windows 실행 파일의 동적 캡처는 하지 않았다. 비용이 드는 외부 서버는 사용하지 않으며, 원본 EXE 정적 제어흐름 + 원본 데이터 + 실패 우선 회귀 + Chromium + GitHub Actions를 근거로 복원한다.
