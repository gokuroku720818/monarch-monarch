# 모나크모나크 V184 — 원본 패리티 기반 및 Action 10 정확한 높이 타깃 복원

## 기준

- V183 LITE Git blob: `d366a1c67bfb97e495cb80be11cb8312390da85d`.
- V183 FULL Git blob: `f3fd01924c227424521664232a53249560d746c2`.
- 사용자 제공 원본 `lm_win.exe` 및 원본 M_032 맵을 정적 대조했다.
- V184부터 `parity/original-parity.json`과 `tools/audit_parity.py`를 추가하여 원본 근거와 구현·테스트를 연결한다.

## V183에서 재현한 차이

원본 M_032의 (x=7,y=13)에는 실제로 두 개의 울타리 쌍이 같은 열에 존재한다.

- 낮은 코어: z=3, 상단 z=4
- 높은 코어: z=38, 상단 z=39

V183의 Action 10 dispatcher는 실행 중 `destructibleCoreAt(a.x,a.y)`로 열 전체를 다시 검색하고 `a.z=core.z`로 목표를 덮어쓴다. 높은 울타리가 제거된 다음 패스에서 낮은 z=3 울타리를 발견해 목표가 z=3으로 바뀌고, 높은 지형의 병사는 높이 조건 때문에 더 이상 작업할 수 없어 Action 10에 남을 수 있다.

실패 우선 검증:
- Node 회귀에서 V183은 선택한 높은 울타리 삭제 뒤 Action 10 종료 조건을 만족하지 못해 실패.
- 실제 Chromium + M_032에서 V183은 높은 울타리 삭제 후 `actionTarget.z`가 **38 → 3**으로 변경되고 Action 10이 유지되는 것을 재현.

## 원본 EXE 근거

- `lm_win.exe 0x43ba75..0x43ba84`: dispatcher가 유닛의 저장된 target 레코드(+0x16)를 Action 10 호출에 직접 전달.
- `lm_win.exe 0x434c57..0x434d45`: Action 10 worker가 전달받은 target에서 x/y/z를 직접 해석해 해당 레벨의 맵 셀을 사용.

따라서 실행 중 같은 x/y 열의 다른 z 구조물을 재검색하는 V183 동작은 제거한다.

## V184 수정

- 명령 발행 시 상단 40/42/44/46 클릭을 대응 하단 odd core로 한 번 정규화하는 기존 동작은 유지.
- Action 10 실행 중에는 저장된 `actionTarget.x/y/z`의 정확한 셀만 검사.
- 저장된 z에 41/43/45/47 코어가 더 이상 없으면 `finishWorkAction()`으로 종료.
- 같은 x/y의 다른 높이 울타리로 자동 재타깃하지 않음.
- 공격력, 병력 소모, 파괴 단계, 높이 허용 범위, 경로, AI, 경제, 맵/오디오 자산은 변경하지 않음.

## 검증

- V183 RED → V184 LITE/FULL Node GREEN.
- Chromium M_032 LITE: 높은 울타리 제거 후 actionCode 1, actionTarget null, 낮은 울타리 41+40 그대로, page/runtime error 0.
- FULL은 내장 음악 데이터가 매우 커 브라우저 테스트 하네스에서 `monarch-original-midi-playback` 스크립트 내용만 제거한 뒤 동일 게임 엔진을 검사했으며 같은 결과를 확인. 실제 FULL 원본 파일 자체는 Node 회귀와 자산 안정성 검사에 사용.
- V183→V184를 Action 10 패치와 버전표기만 역변환하면 전체 HTML이 V183과 바이트 동일.
- STAGES와 SOUND_DATA 동일.
- 내장 Base64 payload 23개 전부 V183과 해시 동일.
- V184 LITE에서 75개 스테이지를 각각 10 simulation pass 실행: 75/75 완료, invariant failure 0, runtime/page error 0.
- 기존 V173~V183 focused regressions와 원본 75 MAP/제목·장군 마커/WAV 159개 검사는 GitHub Actions release gate에 포함.

## 생성 결과

로컬 검증 빌드 Git blob:
- V184 LITE: `78ace5e2a00d34510dba3a0606a0fcd8aa022cca`
- V184 FULL: `957a10266f4d4aeee5ab8c486b977ea1058053d1`

## 한계

- 원본 Windows 실행 파일과 동일 입력을 장시간 자동 재생하여 AI·경제·전투·승패를 동적으로 1:1 비교한 상태는 아직 아니다.
- GitHub 저장소에는 BGM 포함 FULL HTML을 커밋하지 않으므로 GitHub Actions는 배포 대상 LITE를 직접 생성·검증한다. FULL은 로컬 exact-blob 패치 및 별도 회귀/자산 검증 대상이다.
- 75-stage invariant 검사는 현재 각 맵 10 pass의 bounded smoke이며 장시간 동등성 증명이 아니다.
