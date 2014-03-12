#pragma once

#include <writer.hh>
#include <reporter.hh>
#include <file-parser.hh>
#include <filter.hh>

#include <string>
#include <unordered_map>

namespace kcov
{
	class IFileParser;
	class IReporter;
	class IOutputHandler;

	class WriterBase : public IFileParser::ILineListener, public IWriter
	{
	protected:
		WriterBase(IFileParser &elf, IReporter &reporter, IOutputHandler &output);

		class File
		{
		public:
			typedef std::unordered_map<unsigned int, std::string> LineMap_t;

			File(const std::string &filename);

			std::string m_name;
			std::string m_fileName;
			std::string m_outFileName;
			LineMap_t m_lineMap;
			unsigned int m_codeLines;
			unsigned int m_executedLines;
			unsigned int m_lastLineNr;

			static int fileNameCount;

		private:
			void readFile(const std::string &filename);
		};

		typedef std::unordered_map<std::string, File *> FileMap_t;


		/* Called when the ELF is parsed */
		void onLine(const std::string &file, unsigned int lineNr, unsigned long addr);


		void *marshalSummary(IReporter::ExecutionSummary &summary,
				const std::string &name, size_t *sz);

		bool unMarshalSummary(void *data, size_t sz,
				IReporter::ExecutionSummary &summary,
				std::string &name);

		void setupCommonPaths();

		void stop();

		IFileParser &m_fileParser;
		IReporter &m_reporter;
		FileMap_t m_files;
		FileMap_t m_nonExistingFiles;
		std::string m_commonPath;
		IFilter &m_filter;
	};
}
