
import layers
import logging
import subprocess
import symbols


_log = logging.getLogger("lvl")


class STAnalysis:
    def __init__(self, symbolTable):
        self._symbolTable = symbolTable
        self._reportedUndefinedSymbols = []

    def analyzeLayers(self):
        for layer in layers.LAYERS_ORDERING:
            if layers.LAYERS[layer].get("skipAnalysis"):
                continue
            _log.info("Analyzing layer '%s' ..." % layer)
            self._analyzeLayer(layer)
            _log.info("... Done.")

    def _analyzeLayer(self, layer):
        referencedSymbols = self._symbolTable.symbolsReferencedInLayer(layer)
        _log.debug("%d symbols referenced in this layer" % len(referencedSymbols))
        undefinedSymbols = []
        for symbol in referencedSymbols:
            if symbol not in undefinedSymbols and not self._symbolTable.symbolDefinedBeforeReferenced(symbol, layer):
                undefinedSymbols.append(symbol)

        _log.info("%d undefined symbols found." % len(undefinedSymbols))
        if not undefinedSymbols:
            return

        outputFileName = "UndefinedSymbols-%s" % layer
        _log.info("Storing the undefined symbols report into '%s'" % outputFileName)
        with open(outputFileName, "w") as outputFile:
            self._reportUndefinedSymbols(undefinedSymbols, outputFile)

    def _reportUndefinedSymbols(self, undefinedSymbols, outputFile):
        outputFile.write("%d undefined symbols found.\n\n" % len(undefinedSymbols))
        for symbol in undefinedSymbols:
            outputFile.write("Undefined symbol `%s`\n" % self._demangledSymbol(symbol))
            outputFile.write("  mangled: %s\n" % symbol)

            indentedWrite = lambda x: outputFile.write("    %s\n" % x)
            outputFile.write("  libraries that define the symbol:\n")
            map(indentedWrite, set(self._symbolTable.librariesDefiningSymbol(symbol)))
            outputFile.write("  libraries referencing the symbol:\n")
            map(indentedWrite, set(self._symbolTable.librariesReferencingSymbol(symbol)))
            outputFile.write("  object files that reference the symbol:\n")
            map(indentedWrite, set(self._symbolTable.objectFilesReferencingSymbol(symbol)))
            outputFile.write("\n")

    def _demangledSymbol(self, symbol):
        command = ["c++filt", symbol]
        cxxfiltProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = cxxfiltProcess.communicate()
        return stdout.rstrip()
