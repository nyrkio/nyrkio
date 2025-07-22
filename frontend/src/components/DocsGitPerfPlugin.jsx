import { useEffect, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

export const DocsGitPerfPlugin = () => {
  return (
    <>
      <div className="row mt-4 m-2 p-0 col-lg-10">
        <h1>git-perf plugin</h1>
        <p>This is an experimental utility that adds a <code>git perf</code> command to your beloved git. Initially supported commands are: <code>git perf blame</code>, <code>git perf log</code>, <code>git perf status</code>. </p>
        <p>git-perf plugin will extend your normal git output with performance data from Nyrkiö's <a href="https://nyrkio.com/openapi#/default/changes_per_commit_api_v0_changes_perCommit__test_name_prefix__get"><code>changes/perCommit</code></a> API call. You need to be first using Nyrkiö to benefit from git-perf plugin. And Initially only repositories with <a href="/public/">public performance results</a> are supported. (So to test, you can clone a TigerBeetle or Turso repo.)</p>
        <h2>Installation</h2>

        <pre><code>curl https://raw.githubusercontent.com/nyrkio/git-perf/refs/heads/main/src/git-perf > $HOME/bin/git-perf<br />
        chmod a+x $HOME/bin/git-perf</code></pre>

        <h2>Example</h2>

        <pre>$ git perf log<br />
        ...<br />
        commit f24e254ec6c77e166791461111c7747f33334f0a<br />
        Author: Pekka Enberg<br />
        Date:   Thu Jul 10 14:28:38 2025 +0300<br />
        <br />
        core/translate: Fix "misuse of aggregate function" error message<br />
        <br />
        ```<br />
        sqlite> CREATE TABLE test1(f1, f2);<br />
        sqlite> SELECT SUM(min(f1)) FROM test1;<br />
        Parse error: misuse of aggregate function min()<br />
        SELECT SUM(min(f1)) FROM test1;<br />
        ^--- error here<br />
        ```<br />
        <br />
        Spotted by SQLite TCL tests.<br />
        <br />
        commit 6749af7037f9f1895dedff45dd28ab08f40f9a9f<br />
        Merge: 7a259957 89b0574f<br />
        Author: Pekka Enberg<br />
        Date:   Thu Jul 10 14:02:57 2025 +0300<br />
        <br />
        Merge 'core/translate: Return error if SELECT needs tables and there are non<br />
        <br />
        Fixes https://github.com/tursodatabase/turso/issues/1972<br />
        <br />
        Reviewed-by: Jussi Saurio<br />
        <br />
        Closes #2023<br />
        <br />
        perf change:           https://nyrk.io/gh/tursodatabase%252Fturso/main<br />
        turso/main/Prepare__SELECT_1_/limbo_parse_query/SELECT_1:<br />
        time: +64.63 %   1.2342->2.0319<br />
        <br />
        commit 7a259957ac6fc1fe3484a5356968fd3a70c61c96<br />
        Merge: 1333fc88 832f9fb8<br />
        Author: Pekka Enberg<br />
        Date:   Thu Jul 10 13:54:15 2025 +0300<br />
        <br />
        Merge 'properly set last_checksum after recovering wal' from Pere Diaz Bou<br />
        <br />
        We store `last_checksum` to do cumulative checksumming. After reading<br />
        wal for recovery, we didn't set last checksum properly in case there<br />
        were no frames so this cause us to not initialize last_checksum<br />
        properly.<br />
        <br />
        Reviewed-by: Jussi Saurio<br />
        <br />
        Closes #2030</pre>

        <p>The middle commit introduced a +64% perf regression for one benchmark.</p>

        <pre>$ git perf blame core/storage/btree.rs<br />
        d688cfd54↑ core/storage/btree.rs (pedrocarlo       2025-05-31 23:24:27 -0300    1) use tracing::#123;instrument, Level#125;;<br />
        d688cfd54↑ core/storage/btree.rs (pedrocarlo       2025-05-31 23:24:27 -0300    2)<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300    3) use crate::#123;<br />
        b1073da4a  core/storage/btree.rs (Jussi Saurio     2025-04-13 15:17:55 +0300    4)     schema::Index,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300    5)     storage::#123;<br />
        133d49872  core/storage/btree.rs (Jussi Saurio     2025-06-18 12:17:48 +0300    6)         header_accessor,<br />
        5827a3351  core/storage/btree.rs (Zaid Humayun     2025-05-28 20:39:18 +0530    7)         pager::#123;BtreePageAllocMode, Pager#125;,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300    8)         sqlite3_ondisk::#123;<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300    9)             read_u32, read_varint, BTreeCell, PageContent, PageType, TableInteriorCell,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   10)             TableLeafCell,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   11)         #125;,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   12)     #125;,<br />
        5bd47d746↓ core/storage/btree.rs (pedrocarlo       2025-05-16 14:38:01 -0300   13)     translate::#123;collate::CollationSeq, plan::IterationDirection#125;,<br />
        fa442ecd6  core/storage/btree.rs (Pekka Enberg     2025-07-03 13:13:58 +0300   14)     turso_assert,<br />
        b0c64cb4d↑ core/storage/btree.rs (Pere Diaz Bou    2025-06-03 14:28:19 +0200   15)     types::#123;IndexKeyInfo, IndexKeySortOrder, ParseRecordState#125;,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   16)     MvCursor,<br />
        51ad827f1  core/storage/btree.rs (Pere Diaz Bou    2024-11-19 17:56:24 +0100   17) #125;;<br />
        7cb7eb4e6  core/storage/btree.rs (Krishna Vishal   2025-02-07 01:15:21 +0530   18)<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   19) use crate::#123;<br />
            11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   20)     return_corrupt,<br />
        e3f71259d↓ core/storage/btree.rs (Pekka Enberg     2025-05-15 09:41:59 +0300   21)     types::#123;compare_immutable, CursorResult, ImmutableRecord, RefValue, SeekKey, SeekOp, Value#125;,<br />
        11782cbff  core/storage/btree.rs (Pekka Enberg     2025-04-10 07:52:10 +0300   22)     LimboError, Result,<br />
        8642d416c⇊ core/storage/btree.rs (Pere Diaz Bou    2025-03-25 09:49:22 +0100   23) #125;;<br />
        05621e328  core/btree.rs         (Pekka Enberg     2023-08-30 20:24:22 +0300   24)<br />
        99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   25) use super::#123;<br />
            99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   26)     pager::PageRef,<br />
        99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   27)     sqlite3_ondisk::#123;<br />
            99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   28)         write_varint_to_vec, IndexInteriorCell, IndexLeafCell, OverflowCell, DATABASE_HEADER_SIZE,<br />
        99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   29)         MINIMUM_CELL_SIZE,<br />
        99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   30)     #125;,<br />
        99e0cf060⇈ core/storage/btree.rs (meteorgan        2025-07-08 22:55:25 +0800   31) #125;;</pre>

        <p>The commits that caused performance changes are decorated with a up ↑ or down ↓ arrow. A double arrow means the change was larger than 10%. Note however that often there are multiple tests that fail and in that case it is arbitrary which one was used to draw the arrow symbol.</p>

        <pre>$ git perf status<br />
        On branch main<br />
        Your branch is up to date with 'upstream/main'.<br />
        <br />
        nothing to commit, working tree clean<br />
        <br />
        git@github.com:tursodatabase/turso.git/main: 208 commits flagged as either a regression or improvement<br />
        The most recent perf change is cb163fc at 2025-07-17 13:56:49: sys:0.001<br />
        290 metrics across 148 tests reported 1686 changes.<br />
        The test 'clickbench/limbo/main/29_SELECT_Title__COUNT____AS_PageViews_FROM_hits_W' caused 19 of above changes.<br />
        For more details, see https://nyrk.io/gh/tursodatabase%252Fturso/main</pre><br />


      </div>
    </>
  );
};

