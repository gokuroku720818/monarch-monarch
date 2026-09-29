# 모나크모나크 V188 — 울타리 제거와 Action 10 종료의 동일 패스 복원

## 기준

- V187 LITE Git blob: `2e91307fbff652dcd1b2010691c7441e335b35ab`.
- V187 FULL Git blob: `b9b856a83bc07aa62d57d6d636b00568cdc707f7`.
- V188 기능 변경은 Action 10이 DF0 울타리 코어/캡을 실제로 제거한 바로 그 dispatcher pass에서 작업 종료/계속 판정을 실행하도록 하는 한 지점으로 한정한다.

## V187에서 확인한 차이

V187은 정확한 x/y/z 울타리만 파괴하도록 복원했지만, `attackDestructible()`이 마지막 코어를 제거한 뒤에도 해당 pass에서는 `continue`로 빠졌다. 따라서 물리적으로 울타리가 이미 사라졌는데 Action 10과 actionTarget은 한 simulation pass 더 남았다가 다음 pass에서 정리됐다.

## 원본 EXE 근거

- `lm_win.exe 0x434da2..0x434e4f`: Action 10은 작업량/DF가 0인 제거 경로에서 코어와 캡을 지우고 효과음을 재생한 뒤 return 0.
- `0x434e54..0x435030`: 아직 파괴가 끝나지 않은 단계에서는 구조물 상태를 갱신하고 return 3.
- `0x43ba75..0x43bacb`: dispatcher는 worker return 3일 때만 완료 처리를 건너뛰고, 그 외 반환값은 즉시 `0x43bded`의 완료/계속 처리로 진입.
- `0x43bded..0x43be63`: 완료 handler가 continue/wait/normal 작업 상태를 같은 처리 pass 안에서 정리.

따라서 마지막 울타리 제거와 Action 10 종료 사이에 추가 simulation pass가 들어가는 V187 동작은 원본 return-code 흐름과 다르다.

## V188 수정

`attackDestructible(u,a)` 직후 정확한 저장 target 셀 `tileAt(ax,ay,az)`가 0이 되었고 유닛이 살아 있으면 즉시 `finishWorkAction(u)`을 호출한다.

- 정확한 z 유지(V184) 그대로 유지.
- 자기 생산기지 제외(V187) 그대로 유지.
- 미완성 울타리의 단계별 damage/return-3 성격은 변경하지 않음.
- 다른 전투·경제·AI·맵·오디오 데이터는 변경하지 않음.

## 실패 우선 검증

- V187 RED: 테스트용 마지막 울타리 제거 후 같은 dispatcher pass의 `finishWorkAction()` 호출 횟수는 0, Action 10이 한 pass 더 살아 있음.
- V188 GREEN: 제거가 발생한 동일 dispatcher pass에서 `finishWorkAction()` 1회, actionCode가 10에서 해제되고 actionTarget이 null.

## Chromium 검증

실제 V188 엔진에서 DF0 fence core/cap을 두고 Action 10을 실행했다. 첫 update는 방향 보정만 수행할 수 있으므로 최대 4 pass를 추적하고 **구조물이 실제로 0이 된 바로 그 pass**를 검사했다.

- LITE: 제거 pass에서 core=0, cap=0, actionCode!=10, target=null, runtime/page error 0.
- FULL: 테스트 하네스에서 대용량 MIDI playback script만 제거하고 동일 게임 엔진을 실행해 같은 결과 확인.
- V187의 연속 생산기지 파괴 자기기지 제외 Chromium 회귀도 V188에서 계속 통과.

## 자산 및 안정성

- V188 코드 한 지점 + 버전 표기만 역변환하면 V187 HTML과 전체 바이트 동일.
- STAGES 동일.
- SOUND_DATA 동일.
- 내장 Base64 payload 23개 동일.
- V188 LITE 75개 스테이지 × 각 10 simulation pass: 75/75, invariant/runtime/page error 0.

## 생성 결과

- V188 LITE Git blob: `dd5e3442c36bf4b7cd14377b8990379dfed534f7`.
- V188 LITE SHA-256: `ddcc5e6d55328dce8b0e6bfd118422a8e6eb37a8501c69513af85ee42aa56ec9`.
- V188 FULL Git blob: `5a9e6081f43b8a0a8a7b85e4e82fc498b50afbdb`.
- V188 FULL SHA-256: `7dec88ce3d4fefba32b413a4e237779d342542edd04bf669e74c4b737e719c02`.
- V188 complete ZIP SHA-256: `0c501b9aae02314dbcfcdd50df4ee45d7534bfbf3826bb68c70f809e888c8286`.

## GitHub Actions 검증

- workflow run `36502668907`: **success**.
- exact V187 blob 생성, parity manifest/audit, 원본 75 MAP·제목/장군·WAV 159개, V173~V187 focused regressions, V188 same-pass Node/Chromium 회귀, V187 자기기지 제외 browser 회귀, 자산 안정성, 75-stage invariant, JS syntax 모두 success.
- CI staging branch `index.html`과 `monarch_v188_lite.html` Git blob은 모두 `dd5e3442c36bf4b7cd14377b8990379dfed534f7`로 로컬 검증 LITE와 일치.

## 한계

원본 Windows 실행 파일과 같은 입력을 장시간 자동 재생하는 전체 동적 비교는 아직 완료하지 않았다. 비용이 드는 외부 서버는 사용하지 않으며, 원본 EXE 정적 제어흐름 + 원본 데이터 + 실패 우선 회귀 + Chromium + GitHub Actions를 근거로 복원한다.
