from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.util import header
from claon_admin.config.auth import get_subject
from claon_admin.container import Container, db
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterRequestDto, CenterResponseDto
from claon_admin.model.enum import OAuthProvider
from claon_admin.model.user import SignInRequestDto, LectorRequestDto, JwtResponseDto, \
    IsDuplicatedNicknameResponseDto, LectorResponseDto
from claon_admin.service.user import UserService

router = APIRouter()


@cbv(router)
class AuthRouter:
    @inject
    def __init__(self,
                 user_service: UserService = Depends(Provide[Container.user_service])):
        self.user_service = user_service

    @router.post('/{provider}/sign-in', response_model=JwtResponseDto)
    async def sign_in(self,
                      response: Response,
                      provider: OAuthProvider,
                      dto: SignInRequestDto,
                      session: AsyncSession = Depends(db.get_db)):
        jwt_dto: JwtResponseDto = await self.user_service.sign_in(session, provider, dto)
        header.add_jwt_tokens(response, jwt_dto.access_token, jwt_dto.refresh_token)
        return jwt_dto

    @router.post('/center/sign-up', response_model=CenterResponseDto)
    async def center_sign_up(self,
                             dto: CenterRequestDto,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.sign_up_center(session, subject, dto)

    @router.post('/lector/sign-up', response_model=LectorResponseDto)
    async def lector_sign_up(self,
                             dto: LectorRequestDto,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.sign_up_lector(session, subject, dto)

    @router.get('/nickname/{nickname}/is-duplicated', response_model=IsDuplicatedNicknameResponseDto)
    async def is_duplicated_nickname(self,
                                     nickname: str,
                                     session: AsyncSession = Depends(db.get_db)):
        return await self.user_service.check_nickname_duplication(session, nickname)
