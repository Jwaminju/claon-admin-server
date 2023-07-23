from datetime import date
from typing import List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_pagination import Params
from fastapi_utils.cbv import cbv

from claon_admin.common.util.auth import CenterAdminUser, CurrentUser
from claon_admin.common.util.pagination import Pagination
from claon_admin.container import Container
from claon_admin.model.center import CenterNameResponseDto, CenterResponseDto, CenterUpdateRequestDto, \
    CenterBriefResponseDto, CenterCreateRequestDto, CenterFeeDetailResponseDto, CenterFeeDetailRequestDto, \
    CenterFeeResponseDto
from claon_admin.common.enum import CenterUploadPurpose, CenterFeeUploadPurpose, CenterMemberSearchOrder, \
    CenterMemberStatus, MembershipStatusSearchOrder, MembershipStatus
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.membership import CenterMemberSummaryResponseDto, CenterMemberBriefResponseDto, \
    CenterMemberDetailResponseDto, MembershipSummaryResponseDto, MembershipResponseDto
from claon_admin.model.post import PostResponseDto, PostSummaryResponseDto, PostCommentResponseDto, PostBriefResponseDto
from claon_admin.model.review import ReviewSummaryResponseDto, ReviewAnswerResponseDto, ReviewAnswerRequestDto, \
    ReviewBriefResponseDto
from claon_admin.model.schedule import ScheduleRequestDto, ScheduleBriefResponseDto, ScheduleResponseDto
from claon_admin.service.center import CenterService
from claon_admin.service.post import PostService
from claon_admin.service.review import ReviewService

router = APIRouter()


@cbv(router)
class CenterRouter:
    @inject
    def __init__(self,
                 center_service: CenterService = Depends(Provide[Container.center_service]),
                 post_service: PostService = Depends(Provide[Container.post_service]),
                 review_service: ReviewService = Depends(Provide[Container.review_service])):
        self.center_service = center_service
        self.post_service = post_service
        self.review_service = review_service

    @router.get('/name/{name}', response_model=List[CenterNameResponseDto])
    async def get_name(self,
                       name: str):
        return await self.center_service.find_centers_by_name(name=name)

    @router.get('/{center_id}', response_model=CenterResponseDto)
    async def find_by_id(self,
                         subject: CenterAdminUser,
                         center_id: str):
        return await self.center_service.find_by_id(subject=subject, center_id=center_id)

    @router.post('/{purpose}/file', response_model=UploadFileResponseDto)
    async def upload(self,
                     subject: CenterAdminUser,
                     purpose: CenterUploadPurpose,
                     file: UploadFile = File(...)):
        return await self.center_service.upload_file(purpose, file)

    @router.get('/', response_model=Pagination[CenterBriefResponseDto])
    async def find_centers(self,
                           subject: CenterAdminUser,
                           params: Params = Depends()):
        return await self.center_service.find_centers(params=params, subject=subject)

    @router.post('/', response_model=CenterResponseDto)
    async def create(self,
                     subject: CurrentUser,
                     dto: CenterCreateRequestDto):
        return await self.center_service.create(subject=subject, dto=dto)

    @router.put('/{center_id}', response_model=CenterResponseDto)
    async def update(self,
                     subject: CenterAdminUser,
                     center_id: str,
                     request_dto: CenterUpdateRequestDto):
        return await self.center_service.update(center_id=center_id, subject=subject, dto=request_dto)

    @router.delete('/{center_id}', response_model=CenterResponseDto)
    async def delete(self,
                     subject: CenterAdminUser,
                     center_id: str):
        return await self.center_service.delete(center_id=center_id, subject=subject)

    @router.get('/{center_id}/posts/{post_id}', response_model=PostResponseDto)
    async def find_post(self,
                        center_id: str,
                        post_id: str):
        pass

    @router.get('/{center_id}/posts/{post_id}/comments', response_model=PostCommentResponseDto)
    async def find_post_comment(self,
                                center_id: str,
                                post_id: str):
        pass

    @router.get('/{center_id}/posts', response_model=Pagination[PostBriefResponseDto])
    async def find_posts_by_center(self,
                                   subject: CenterAdminUser,
                                   center_id: str,
                                   start: date,
                                   end: date,
                                   hold_id: str | None = None,
                                   params: Params = Depends()):
        return await self.post_service.find_posts_by_center(
            subject=subject,
            params=params,
            hold_id=hold_id,
            center_id=center_id,
            start=start,
            end=end
        )

    @router.get('/{center_id}/reviews', response_model=Pagination[ReviewBriefResponseDto])
    async def find_reviews_by_center(self,
                                     subject: CenterAdminUser,
                                     center_id: str,
                                     start: date,
                                     end: date,
                                     tag: str | None = None,
                                     is_answered: bool | None = None,
                                     params: Params = Depends()):
        return await self.review_service.find_reviews_by_center(
            subject=subject,
            params=params,
            center_id=center_id,
            start=start,
            end=end,
            tag=tag,
            is_answered=is_answered
        )

    @router.get('/{center_id}/posts/summary', response_model=PostSummaryResponseDto)
    async def find_posts_summary_by_center(self,
                                           subject: CenterAdminUser,
                                           center_id: str):
        return await self.post_service.find_posts_summary_by_center(subject, center_id)

    @router.get('/{center_id}/reviews/summary', response_model=ReviewSummaryResponseDto)
    async def find_reviews_summary_by_center(self,
                                             subject: CenterAdminUser,
                                             center_id: str):
        return await self.review_service.find_reviews_summary_by_center(subject, center_id)

    @router.post('/{center_id}/reviews/{review_id}', response_model=ReviewAnswerResponseDto)
    async def create_review_answer(self,
                                   subject: CenterAdminUser,
                                   request_dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        return await self.review_service.create_review_answer(subject, request_dto, center_id, review_id)

    @router.put('/{center_id}/reviews/{review_id}', response_model=ReviewAnswerResponseDto)
    async def update_review_answer(self,
                                   subject: CenterAdminUser,
                                   request_dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        return await self.review_service.update_review_answer(subject, request_dto, center_id, review_id)

    @router.delete('/{center_id}/reviews/{review_id}')
    async def delete_review_answer(self,
                                   subject: CenterAdminUser,
                                   center_id: str,
                                   review_id: str):
        return await self.review_service.delete_review_answer(subject, center_id, review_id)

    @router.get('/{center_id}/fees', response_model=CenterFeeDetailResponseDto)
    async def find_center_fees(self,
                               subject: CenterAdminUser,
                               center_id: str):
        return await self.center_service.find_center_fees(subject, center_id)

    @router.post('/{center_id}/fees', response_model=CenterFeeDetailResponseDto)
    async def update_center_fees(self,
                                 subject: CenterAdminUser,
                                 center_id: str,
                                 request_dto: CenterFeeDetailRequestDto):
        return await self.center_service.update_center_fees(subject, center_id, request_dto)

    @router.delete('/{center_id}/fees/{center_fee_id}', response_model=CenterFeeResponseDto)
    async def delete_center_fee(self,
                                subject: CenterAdminUser,
                                center_id: str,
                                center_fee_id: str):
        return await self.center_service.delete_center_fee(
            subject=subject,
            center_id=center_id,
            center_fee_id=center_fee_id
        )

    @router.post('/{center_id}/fees/{purpose}/file', response_model=UploadFileResponseDto)
    async def upload_membership_image(self,
                                      subject: CenterAdminUser,
                                      center_id: str,
                                      purpose: CenterFeeUploadPurpose,
                                      file: UploadFile = File(...)):
        pass

    @router.get('/{center_id}/members/summary', response_model=CenterMemberSummaryResponseDto)
    async def find_members_summary_by_center(self,
                                             subject: CurrentUser,
                                             center_id: str):
        pass

    @router.get('/{center_id}/members', response_model=Pagination[CenterMemberBriefResponseDto])
    async def find_members_by_name(self,
                                   subject: CurrentUser,
                                   center_id: str,
                                   nickname: str | None = None,
                                   order: CenterMemberSearchOrder | None = None,
                                   member_status: CenterMemberStatus | None = None):
        pass

    @router.get('/{center_id}/members/{nickname}', response_model=CenterMemberDetailResponseDto)
    async def find_members_detail_by_id(self,
                                        subject: CurrentUser,
                                        center_id: str,
                                        nickname: str):
        pass

    @router.get('/{center_id}/memberships/summary', response_model=MembershipSummaryResponseDto)
    async def find_memberships_summary_by_center(self,
                                                 subject: CurrentUser,
                                                 center_id: str):
        pass

    @router.get('/{center_id}/memberships', response_model=Pagination[MembershipResponseDto])
    async def find_memberships_by_center(self,
                                         subject: CurrentUser,
                                         center_id: str,
                                         nickname: str | None = None,
                                         order: MembershipStatusSearchOrder | None = None,
                                         membership_status: MembershipStatus | None = None):
        pass

    @router.get('/{center_id}/schedules', response_model=List[ScheduleBriefResponseDto])
    async def find_schedules_by_center(self,
                                       subject: CenterAdminUser,
                                       center_id: str):
        pass

    @router.get('/{center_id}/schedules/{schedule_id}', response_model=ScheduleResponseDto)
    async def find_schedule_detail_by_id(self,
                                         subject: CenterAdminUser,
                                         center_id: str,
                                         schedule_id: str):
        pass

    @router.post('/{center_id}/schedules', response_model=ScheduleResponseDto)
    async def create_schedule(self,
                              subject: CenterAdminUser,
                              center_id: str,
                              request_dto: ScheduleRequestDto):
        pass

    @router.put('/{center_id}/schedules/{schedule_id}', response_model=ScheduleResponseDto)
    async def update_schedule(self,
                              subject: CenterAdminUser,
                              center_id: str,
                              schedule_id: str,
                              request_dto: ScheduleRequestDto):
        pass

    @router.delete('/{center_id}/schedules/{schedule_id}')
    async def delete_schedule(self,
                              subject: CenterAdminUser,
                              center_id: str,
                              schedule_id: str):
        pass
