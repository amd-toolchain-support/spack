# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
# ----------------------------------------------------------------------------\
from spack.pkg.builtin.libflame import LibflameBase


class Amdlibflame(LibflameBase):
    """libFLAME (AMD Optimized version) is a portable library for
    dense matrix computations, providing much of the functionality
    present in Linear Algebra Package (LAPACK). It includes a
    compatibility layer, FLAPACK, which includes complete LAPACK
    implementation.

    The library provides scientific and numerical computing communities
    with a modern, high-performance dense linear algebra library that is
    extensible, easy to use, and available under an open source
    license. libFLAME is a C-only implementation and does not
    depend on any external FORTRAN libraries including LAPACK.
    There is an optional backward compatibility layer, lapack2flame
    that maps LAPACK routine invocations to their corresponding
    native C implementations in libFLAME. This allows legacy
    applications to start taking advantage of libFLAME with
    virtually no changes to their source code.

    In combination with BLIS library which includes optimizations
    for the AMD EPYC processor family, libFLAME enables running
    high performing LAPACK functionalities on AMD platform.
    """

    _name = 'amdlibflame'
    homepage = "http://developer.amd.com/amd-cpu-libraries/blas-library/#libflame"
    git = "https://github.com/amd/libflame.git"

    maintainers = ['amd-toolchain-support']

    version('3.0.1', sha256='b2fbe4cc3009b114b7c9b80a1759fefbfb12a7b1b5751a7f377e4f39d6ace679')
    version('3.0', sha256='d94e08b688539748571e6d4c1ec1ce42732eac18bd75de989234983c33f01ced')
    version('2.2', sha256='12b9c1f92d2c2fa637305aaa15cf706652406f210eaa5cbc17aaea9fcfa576dc')

    variant('ilp64', default=False, description='Build with ILP64 support')

    conflicts('+ilp64', when="@:3.0.0",
              msg="ILP64 is supported from 3.0.1 onwards")

    def url_for_version(self, version):
        if version == Version('3.0.1'):
            return "http://aocl.amd.com/data/spack/amdlibflame/3.0.1.tar.gz"
        else:
            return "https://github.com/amd/libflame/archive/3.0.tar.gz"

    patch('aocc-2.2.0.patch', when="@:2.999", level=1)
    patch('cray-compiler-wrapper.patch')

    provides('flame@5.2', when='@2:')

    @property
    def lapack_libs(self):
        """find lapack_libs function"""
        shared = True if '+shared' in self.spec else False
        return find_libraries(
            'libflame', root=self.prefix, shared=shared, recursive=True
        )

    def configure_args(self):
        """configure_args function"""
        args = super(Amdlibflame, self).configure_args()
        args.append("--enable-external-lapack-interfaces")

        """To enabled Fortran to C calling convention for
        complex types when compiling with aocc flang"""
        if "@3.0: %aocc" in self.spec:
            args.append("--enable-f2c-dotc")

        if "@3.0.1: +ilp64" in self.spec:
            args.append("--enable-ILP64")

        return args

    def install(self, spec, prefix):
        """make install function"""
        # make install in parallel fails with message 'File already exists'
        make("install", parallel=False)
