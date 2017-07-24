INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_BODE bode)

FIND_PATH(
    BODE_INCLUDE_DIRS
    NAMES bode/api.h
    HINTS $ENV{BODE_DIR}/include
        ${PC_BODE_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    BODE_LIBRARIES
    NAMES gnuradio-bode
    HINTS $ENV{BODE_DIR}/lib
        ${PC_BODE_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(BODE DEFAULT_MSG BODE_LIBRARIES BODE_INCLUDE_DIRS)
MARK_AS_ADVANCED(BODE_LIBRARIES BODE_INCLUDE_DIRS)

