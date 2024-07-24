# we need to include new view here
from .activity import GetActivityList
from .history import UpdateHistory, UpdateHistorys, GetHistoryList, MoveToNewPerson, GetChartValue, DeleteHistory, GetHistorySumup, ReportExcelHistory, UseAsSample, GetAttendancesRealtime
from .annotation import UpdateAnnotation, UpdateAnnotations, GetAnnotationList, MoveToNewPerson, GetChartValue, DeleteAnnotation, GetAnnotationSumup, ReportExcelAnnotation, UseAsSample, GetAttendancesRealtime
from .attendance import ReportExcelAttendance
from .config import CreateSearchOption, UpdateSearchOption, GetSearchOption, GetSearchOptionList
from .building import UpdateBuilding, GetBuildingList, DeleteBuilding
from .database import UpdateDatabase
from .diag import Compare, DrawLandmark, FindDirNotExistInDB, FaceDirection, CheckBrightness
from .idcard import ExtractIDCard
from .label import UpdateLabel, GetLabelList, DeleteLabel
from .loginsession import GetLoginSession, verifyToken, Redirect
from .log import GetLogList
from .os import SendCommand
from .patrol import GetPatrolList, FinishPatrol
from .person import GetPersonList, GetPerson, DeletePerson, GetImageList, UpdatePerson, GetSimilarPerson, AddPerson, MergePerson, GetMaxPerson, ReportExcelPerson, Checkin, DeleteImage
from .persongroup import GetPersonGroupList, UpdatePersonGroup, GetPersonGroup, RemovePersonGroup
from .phone import SendPhoneInfo, GetPhoneList, UpdatePhone
from .route import UpdateRoute, DeleteRoute, GetRouteList, GetRoute
from .systeminfo import GetSystemInfo, IsServerRunning, BackupDB
from .testcase import TestDlib
from .user import login, logout, GetUser, ChangePassword, GetUserList, ResetPassword, UpdateUser, RemoveUser, Register, GetOrgList, SendEmailResetPassword