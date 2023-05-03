from datetime import date
from typing import Optional

from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.model.post import PostBriefResponseDto
from claon_admin.schema.center import PostRepository, CenterRepository


class CenterService:
    def __init__(self,
                 center_repository: CenterRepository,
                 post_repository: PostRepository,
                 pagination_factory: PaginationFactory):
        self.center_repository = center_repository
        self.post_repository = post_repository
        self.pagination_factory = pagination_factory

    async def find_posts_by_center(self,
                                   session: AsyncSession,
                                   params: Params,
                                   center_id: str,
                                   hold_id: Optional[str],
                                   start: date,
                                   end: date):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        if hold_id is not None:
            hold_ids = [h.id for h in center.holds]
            if hold_id not in hold_ids:
                raise BadRequestException(
                    ErrorCode.DATA_DOES_NOT_EXIST,
                    "해당 홀드가 암장에 존재하지 않습니다."
                )

        pages = await self.post_repository.find_posts_by_center(
            session=session,
            params=params,
            center_id=center_id,
            hold_id=hold_id,
            start=start,
            end=end
        )

        return await self.pagination_factory.create(PostBriefResponseDto, pages)
