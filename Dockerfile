FROM public.ecr.aws/lambda/python:3.13

# ============================================================
# 1. Chrome 실행에 필요한 시스템 라이브러리
#    (Amazon Linux 2023 베이스라 dnf 사용)
# ============================================================

RUN dnf install -y \
        unzip \
        atk \
        cups-libs \
        gtk3 \
        libXcomposite \
        libXcursor \
        libXdamage \
        libXext \
        libXi \
        libXrandr \
        libXScrnSaver \
        libXtst \
        pango \
        alsa-lib \
        nss \
        at-spi2-atk \
        mesa-libgbm \
    && dnf clean all

# ============================================================
# 2. Chrome for Testing + 버전이 맞는 chromedriver 설치
#    버전을 고정해서 관리한다 (latest를 쓰면 배포할 때마다
#    버전이 달라져서 문제 재현이 어려워짐)
# ============================================================

ARG CHROME_FOR_TESTING_VERSION=131.0.6778.108

RUN curl -Lo /tmp/chrome-linux64.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_FOR_TESTING_VERSION}/linux64/chrome-linux64.zip" \
    && curl -Lo /tmp/chromedriver-linux64.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_FOR_TESTING_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chrome-linux64.zip -d /opt \
    && unzip /tmp/chromedriver-linux64.zip -d /opt \
    && rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip

# crawler.py의 create_driver()가 os.getenv()로 읽는 값과
# 이름이 정확히 일치해야 한다 (Chapter 2 참고)
ENV CHROME_BIN=/opt/chrome-linux64/chrome
ENV CHROMEDRIVER_PATH=/opt/chromedriver-linux64/chromedriver

# Chrome이 프로필/캐시를 저장할 홈 디렉터리를
# Lambda에서 쓰기 가능한 유일한 경로로 지정
ENV HOME=/tmp

# ============================================================
# 3. Python 의존성 설치
# ============================================================

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# ============================================================
# 4. 애플리케이션 코드 복사
# ============================================================

COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY handlers/ ${LAMBDA_TASK_ROOT}/handlers/

CMD ["handlers.pipeline_handler.lambda_handler"]