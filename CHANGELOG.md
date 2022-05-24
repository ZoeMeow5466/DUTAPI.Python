# DUTAPI CHANGE LOG FOR PYTHON

This file will list all version log for modified, add or remove function of DUTAPI.

## 1.4.5

- Remove unnecessary key "gmt" (due to key "date" has already included).
- Add key "position" in GetNews(): Easier get link in key "contenttext".

## 1.4.4

- DateExamInString in subject schedule will be splitted to 2 items (managed by *`__string2ExamSchedule__()`*):
  - `DateExam`: isoformat
  - `RoomExam`: string
- Add Region GMT. This is useful when you host a server which its GMT is different from your computer/region.
  (managed by *`GetRegionGMT()`*)
- All date in json will be returned to isoformat instead of string, so you can use them directly with functions that can be initialized with isoformat string
  (note: **date in *`GetNews()['newslist']`* function won't be affected**).

## 1.4.3

- New function: Get current week (data from dut.udn.vn).
- Move 'GetNews' function to Utils.py (this will also remove file 'GetNews.py'.
- Functions in class 'Session.py' will be work independently (no more class 'Session').

## 1.4.2

[.NET]
- Optimize code line.

## 1.4.1

[.NET]
- Merge `GetNewsGeneral()` and `GetNewsSubject()` together.
  - To `GetNews()`.

## 1.4

- Inital commit for Java.

## 1.3

- Inital commit for Python.
- Delete unneed files for .NET.
- Optimize code :)

## 1.2

- Added feature: Get all subjects fee list.
- Change file and function name: ~~GetScheduleSubject~~ to **GetSubjectsSchedule**.
- Add [CHANGELOG.md](CHANGELOG.md) for all old logs.
- Optimize code.

## 1.1

- Added feature: Get schedule about subjects and examimation.

## 1.0

Inital commit with features:
- Get news general (Nhận thông báo chung).
- Get news subjects (Nhận thông báo lớp học phần).
- Sesion (Phiên, dùng để đăng nhập/đăng xuất/lấy thông tin tài khoản).
