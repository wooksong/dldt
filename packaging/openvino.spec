%bcond_with tizen
%if %{with tizen}
%global debug_package %{nil}
%global __debug_install_post %{nil}

%if "%{?_lib}" == "lib64"
%define _cmake_lib_suffix_flag %{?_cmake_lib_suffix64}
%else
%define _cmake_lib_suffix_flag %{nil}
%endif

%ifarch x86_64
%define _cmake_sse_support_flag -DENABLE_SSE42=1
%else
%define _cmake_sse_support_flag -DENABLE_SSE42=0
%endif

%define _extra_cmake_flags %{_cmake_lib_suffix_flag} %{_cmake_sse_support_flag} -DLINUX_OS_NAME="Tizen %{tizen_full_version}"

%ifarch x86_64 i686 armv7l aarch64

%ifarch x86_64
%define install_arch    intel64
%endif

%ifarch i686
%define install_arch    i686
%endif

%ifarch armv7l
%define install_arch    armv7l
%endif

%ifarch aarch64
%define install_arch    aarch64
%endif

%else
%define install_arch    %{_arch}
%endif

%endif

%define     external_ade_archive        ade-cbe2db61a659c2cc304c3837406f95c39dfa938e
%define     external_ngraph_archive     ngraph-0.22.0-rc.2

Name:           openvino
Summary:        OpenVINO™ Toolkit - Deep Learning Deployment Toolkit
Version:        2019R3
Release:        0
Group:          Development/Libraries
Packager:       Wook Song <wook16.song@samsung.com>
License:        Apache-2.0
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}.manifest
Source1001:     %{external_ade_archive}.tar.gz
Source1002:     %{external_ngraph_archive}.tar.gz
Patch0:         0001-CMake-Do-not-call-get_linux_name-when-LINUX_OS_NAME-.patch
Patch1:         0002-CMake-Add-a-variable-to-resolve-dependency-on-TBB-us.patch
BuildRequires:  cmake
BuildRequires:  pkgconfig(libtbb)
BuildRequires:  pkg-config

%description
OpenVINO™ toolkit, short for Open Visual Inference and Neural network Optimization toolkit,
provides developers with improved neural network performance on a variety of Intel® processors
and helps them further unlock cost-effective, real-time vision applications.
The toolkit enables deep learning inference and easy heterogeneous execution across multiple
Intel® platforms (CPU, Intel® Processor Graphics)—providing implementations across cloud
architectures to edge devices. This open source distribution provides flexibility and
availability to the developer community to innovate deep learning and AI solutions.

%package devel
Summary:        Development package for OpenVINO™ Toolkit
Requires:       %{name} = %{version}-%{release}

%description devel
Development package for Open Visual Inference and Neural network Optimization toolkit.
This contains corresponding header files and static archives.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
cp %{SOURCE1} .
cp %{SOURCE1001} ./inference-engine/thirdparty
cp %{SOURCE1002} ./inference-engine/thirdparty
pushd inference-engine
pushd thirdparty
tar zxf %{external_ade_archive}.tar.gz
mv %{external_ade_archive}/* ade/
tar zxf %{external_ngraph_archive}.tar.gz
mv %{external_ngraph_archive}/* ngraph/
rm -rf *.tar.gz %{external_ade_archive} %{external_ngraph_archive}
popd
rm -rf build && mkdir -p build
pushd build
CFLAGS="${CFLAGS:-%optflags}"; export CFLAGS=${CFLAGS/-Wall/};
CXXFLAGS="${CXXFLAGS:-%optflags}"; export CXXFLAGS=${CXXFLAGS/-Wall/};
FFLAGS="${FFLAGS:-%optflags}"; export FFLAGS=${FFLAGS/-Wall/};
cmake .. \
        -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
        -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
        -DLIB_INSTALL_DIR:PATH=%{_libdir} -DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
        -DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
        %{?_cmake_skip_rpath} \
        -DBUILD_SHARED_LIBS:BOOL=ON \
        -DUSE_TBB_SYSTEM_DEPS=ON -DBUILD_ADE_DOCUMENTATION=OFF -DBUILD_ADE_TUTORIAL=OFF \
        -DBUILD_PKGCONFIG=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DBUILD_TESTS=OFF \
        -DCLDNN__INCLUDE_EXAMPLES=OFF -DCMAKE_BUILD_TYPE=Release -DCOVERAGE=OFF \
        -DDEVELOPMENT_PLUGIN_MODE=OFF -DENABLE_VPU=OFF -DENABLE_ADE_TESTING=OFF \
        -DENABLE_AFFINITY_GENERATOR=OFF -DENABLE_ALTERNATIVE_TEMP=OFF -DENABLE_CLDNN=OFF \
        -DENABLE_CLDNN_BUILD=OFF -DENABLE_CLDNN_TESTS=OFF -DENABLE_CPPCHECK=OFF -DENABLE_CPPLINT=OFF \
        -DENABLE_CPPLINT_REPORT=OFF -DENABLE_CPP_CCT=OFF -DENABLE_DEBUG_SYMBOLS=OFF \
        -DENABLE_FUZZING=OFF -DENABLE_GAPI_TESTS=OFF -DENABLE_GNA=OFF -DENABLE_LTO=OFF \
        -DENABLE_MKL_DNN=OFF -DENABLE_MYRIAD=OFF -DENABLE_MYRIAD_MVNC_TESTS=OFF -DENABLE_MYRIAD_NO_BOOT=OFF \
        -DENABLE_OBJECT_DETECTION_TESTS=ON -DENABLE_OPENCV=OFF -DENABLE_PLUGIN_RPATH=OFF \
        -DENABLE_PROFILING_ITT=OFF -DENABLE_PROFILING_RAW=OFF -DENABLE_PYTHON=OFF -DENABLE_ROCKHOPER=OFF \
        -DENABLE_SAMPLES=OFF -DENABLE_SAMPLES_CORE=OFF -DENABLE_SEGMENTATION_TESTS=OFF -DENABLE_TESTS=ON \
        -DTREAT_WARNING_AS_ERROR=OFF %{_extra_cmake_flags}
popd
popd

%build
pushd inference-engine
pushd build
%{__make} %{?_smp_mflags}
popd
popd

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_libdir}/tbb
pushd inference-engine/bin/%{install_arch}/Release
install -m 644 lib/*.so %{buildroot}%{_libdir}
install -m 644 lib/*.xml %{buildroot}%{_libdir}
install -m 644 lib/*.a %{buildroot}%{_libdir}/tbb
popd
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_includedir}/builders
mkdir -p %{buildroot}%{_includedir}/cpp
mkdir -p %{buildroot}%{_includedir}/details
mkdir -p %{buildroot}%{_includedir}/hetero
mkdir -p %{buildroot}%{_includedir}/multi-device
pushd inference-engine
install -m 644 include/*.h* %{buildroot}%{_includedir}
install -m 644 include/builders/*.h* %{buildroot}%{_includedir}/builders/
install -m 644 include/cpp/*.h* %{buildroot}%{_includedir}/cpp/
install -m 644 include/details/*.h* %{buildroot}%{_includedir}/details/
install -m 644 include/hetero/*.h* %{buildroot}%{_includedir}/hetero/
install -m 644 include/multi-device/*.h* %{buildroot}%{_includedir}/multi-device/
popd

# Block running tests until it is stabilized
#%check
#pushd inference-engine/bin/%{install_arch}/Release
#LD_LIBRARY_PATH=./lib ./InferenceEngineUnitTests
#popd

%post
%{_sbindir}/ldconfig

%postun
%{_sbindir}/ldconfig

%files
%manifest %{name}.manifest
%license LICENSE
%{_libdir}/*.so
%{_libdir}/*.xml

%files devel
%manifest %{name}.manifest
%license LICENSE
%{_libdir}/tbb/*.a
%{_includedir}/*
