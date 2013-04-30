#!/usr/bin/env python

import analysis
import logging
import symbols
import sys


logging.basicConfig(format="[%(levelname)s] %(message)s")
_log = logging.getLogger("lvl")


def main():
    _log.setLevel(logging.DEBUG if "-d" in sys.argv else logging.INFO)

    tableAnalysis = analysis.STAnalysis(symbols.SymbolTable())
    tableAnalysis.analyzeLayers()


if __name__=="__main__":
    main()
