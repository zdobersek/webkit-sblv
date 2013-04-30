
import os
import re
import subprocess


LIBRARY_PATHS = filter(None, [
    os.environ.get("LD_LIBRARY_PATH"),
    "/usr/lib",
    "/usr/lib/x86_64-linux-gnu",
    "/lib/x86_64-linux-gnu",
    os.path.abspath("WebKitBuild/Release/.libs"),
])


OBJECT_FILE_REGEX = re.compile(r"^(?P<file>.*(?:\.o)):$")
SYMBOL_REGEX = re.compile(r"^([ 0-9a-f]{16}) (?P<type>\w) (?P<symbol>.+)$")


class Library:
    def __init__(self, libraryName):
        self.libraryName = libraryName
        self.isSharedLibrary = libraryName.endswith(".so") or libraryName.endswith(".so.6")
        self._libraryPath = self._findLibrary(libraryName)

    def _findLibrary(self, libraryName):
        potentialPaths = map(lambda x: os.path.join(x, libraryName), LIBRARY_PATHS)
        existingPaths = filter(None, map(lambda x: x if os.path.exists(x) else None, potentialPaths))
        assert existingPaths, "Could not find library %s" % libraryName
        return existingPaths[0]

    def definedSymbols(self):
        return self._gatherSymbols(True)

    def referencedSymbols(self):
        return self._gatherSymbols(False)

    def _gatherSymbols(self, defined):
        nmOutput = self._gatherNmOutput(defined).rstrip().split("\n")
        if self.isSharedLibrary:
            return self._parseSharedObjectOutput(nmOutput)
        return self._parseArchiveOutput(nmOutput)

    def _gatherNmOutput(self, defined):
        command = ["nm", "--extern-only"] + (["-D"] if self.isSharedLibrary else []) \
            + (["--defined-only" if defined else "--undefined-only"]) + [self._libraryPath]
        nmProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
        stdout, _ = nmProcess.communicate()
        return stdout

    def _parseSharedObjectOutput(self, outputLines):
        symbolsInSharedObject = { "so": [] }
        for line in outputLines:
            symbolMatch = SYMBOL_REGEX.match(line)
            assert symbolMatch
            symbolsInSharedObject["so"].append(symbolMatch.group("symbol"))

        return symbolsInSharedObject

    def _parseArchiveOutput(self, outputLines):
        symbolsPerObjectFile = {}
        currentObjectFile = None

        for line in outputLines:
            if currentObjectFile is None:
                objectFileMatch = OBJECT_FILE_REGEX.match(line)
                assert objectFileMatch or len(line) is 0
                if objectFileMatch:
                    currentObjectFile = objectFileMatch.group("file")
                    if currentObjectFile not in symbolsPerObjectFile:
                        symbolsPerObjectFile[currentObjectFile] = []
            else:
                symbolMatch = SYMBOL_REGEX.match(line)
                assert symbolMatch or len(line) is 0
                if symbolMatch:
                    assert currentObjectFile in symbolsPerObjectFile
                    symbolsPerObjectFile[currentObjectFile].append(symbolMatch.group("symbol"))
                else:
                    currentObjectFile = None

        return symbolsPerObjectFile
