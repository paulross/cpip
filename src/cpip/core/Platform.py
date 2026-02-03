"""Detect information from the platform this process is running on.

For example:

engun@Pauls-MBP-2  ~/Documents/workspace/cpip (C23)
$ cpp --version
Apple clang version 15.0.0 (clang-1500.0.40.1)
Target: x86_64-apple-darwin22.6.0
Thread model: posix
InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin
(cpip_3.12)
engun@Pauls-MBP-2  ~/Documents/workspace/cpip (C23)
$ echo $?
0
(cpip_3.12)
engun@Pauls-MBP-2  ~/Documents/workspace/cpip (C23)
$ cpp -dM -std=k
error: invalid value 'k' in '-std=k'
note: use 'c89', 'c90', or 'iso9899:1990' for 'ISO C 1990' standard
note: use 'iso9899:199409' for 'ISO C 1990 with amendment 1' standard
note: use 'gnu89' or 'gnu90' for 'ISO C 1990 with GNU extensions' standard
note: use 'c99' or 'iso9899:1999' for 'ISO C 1999' standard
note: use 'gnu99' for 'ISO C 1999 with GNU extensions' standard
note: use 'c11' or 'iso9899:2011' for 'ISO C 2011' standard
note: use 'gnu11' for 'ISO C 2011 with GNU extensions' standard
note: use 'c17', 'iso9899:2017', 'c18', or 'iso9899:2018' for 'ISO C 2017' standard
note: use 'gnu17' or 'gnu18' for 'ISO C 2017 with GNU extensions' standard
note: use 'c2x' for 'Working Draft for ISO C2x' standard
note: use 'gnu2x' for 'Working Draft for ISO C2x with GNU extensions' standard
(cpip_3.12)
engun@Pauls-MBP-2  ~/Documents/workspace/cpip (C23)
$ echo $?
1

$ cpp -E -dM
#define _LP64 1
#define __APPLE_CC__ 6000
#define __APPLE__ 1
#define __ATOMIC_ACQUIRE 2
#define __ATOMIC_ACQ_REL 4
...
#define __unsafe_unretained
#define __weak __attribute__((objc_gc(weak)))
#define __x86_64 1
#define __x86_64__ 1
(cpip_3.12)
engun@Pauls-MBP-2  ~/Documents/workspace/cpip (C23)

NOTE:
$ cpp -E -dM
#define FOO(x, y, z) x+y+z
^D
#define FOO(x,y,z) x+y+z
#define _LP64 1
...

"""
import logging
import pprint
import re
import subprocess
import sys

logger = logging.getLogger(__file__)
LOG_FORMAT_NO_PROCESS = "%(asctime)s - %(filename)24s#%(lineno)-4d - %(levelname)-8s - %(message)s"


class PlatformConfig:
    """This explores the platforms "cpp" for information about versions, standard support etc."""
    # Matches:
    # note: use 'iso9899:199409' for 'ISO C 1990 with amendment 1' standard
    # note: use 'gnu89' or 'gnu90' for 'ISO C 1990 with GNU extensions' standard
    RE_STANDARDS_LINE = re.compile(r"^note: use (.+?) for '(.+)' standard$")

    def __init__(self):
        # Version information.
        subprocess_result = subprocess.run(["cpp", "--version", ], capture_output=True)
        if subprocess_result.returncode:
            raise ValueError(f'"cpp --version" failed with return code {subprocess_result.returncode}')
        subprocess_result_lines = [v.decode() for v in subprocess_result.stdout.split(b'\n')]
        logger.info('Read:\n%s', subprocess_result_lines)
        if len(subprocess_result_lines) < 1:
            raise ValueError(f'"cpp --version" no response in stdout')
        self.cpp_version = subprocess_result_lines[0]
        self.cpp_version_attributes = {}
        for line in subprocess_result_lines[1:]:
            if line:  # Ignore blank lines
                key, value = line.split(':')
                self.cpp_version_attributes[key] = value.strip()

        # Standards support.
        # -std=k is designed to fail.
        subprocess_result = subprocess.run(["cpp", "-dM", "-std=k", ], capture_output=True)
        if subprocess_result.returncode != 1:
            raise ValueError('"cpp --dM -std=k" succeeded when it should have failed')
        subprocess_result_lines = [v.decode() for v in subprocess_result.stderr.split(b'\n')]
        if len(subprocess_result_lines) < 1:
            raise ValueError(f'"cpp --dM -std=k" no response in stdout')
        if not subprocess_result_lines[0].startswith('error:'):
            raise ValueError(f'"cpp --dM -std=k" first line does not start with "error:": {subprocess_result}')
        self.standards_map = {}
        for line in subprocess_result_lines[1:]:
            if line:
                m = self.RE_STANDARDS_LINE.match(line)
                if m is not None:
                    description = m.group(2)
                    stds_str = m.group(1)
                    stds_str = stds_str.replace(', or', ' or')
                    stds_str = stds_str.replace(',', ' or')
                    stds = stds_str.split(' or ')
                    for std in stds:
                        assert std.startswith("'")
                        assert std.endswith("'")
                        key = std[1:-1]
                        if key in self.standards_map:
                            raise ValueError(f'duplicate key "{key}"')
                        self.standards_map[key] = description
                else:
                    logger.error('Can not parse line %s', line)


def main():
    logging.basicConfig(
        level=20, format=LOG_FORMAT_NO_PROCESS, stream=sys.stdout
    )
    plat_config = PlatformConfig()
    print(f'CPP version: {plat_config.cpp_version}')
    print('CPP version attributes:')
    pprint.pprint(plat_config.cpp_version_attributes)
    print('Standards map:')
    pprint.pprint(plat_config.standards_map)
    return 0


if __name__ == '__main__':
    sys.exit(main())
