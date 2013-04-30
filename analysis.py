
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
        for symbol in referencedSymbols:
            if not self._symbolTable.symbolDefinedBeforeReferenced(symbol, layer):
                self._reportUndefinedSymbol(symbol)

    def _reportUndefinedSymbol(self, symbol):
        if symbol in self._reportedUndefinedSymbols:
            return
        self._reportedUndefinedSymbols.append(symbol)

        _log.warning("Undefined symbol `%s`" % self._demangledSymbol(symbol))
        _log.warning("  mangled: %s" % symbol)

        indentedListItemLog = lambda x: _log.warning("    %s" % x)
        _log.warning("  libraries that define the symbol:")
        map(indentedListItemLog, set(self._symbolTable.librariesDefiningSymbol(symbol)))
        _log.warning("  libraries referencing the symbol:")
        map(indentedListItemLog, set(self._symbolTable.librariesReferencingSymbol(symbol)))
        _log.warning("  object files that reference the symbol:")
        map(indentedListItemLog, set(self._symbolTable.objectFilesReferencingSymbol(symbol)))
        _log.warning("")

    def _demangledSymbol(self, symbol):
        command = ["c++filt", symbol]
        cxxfiltProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = cxxfiltProcess.communicate()
        return stdout.rstrip()
