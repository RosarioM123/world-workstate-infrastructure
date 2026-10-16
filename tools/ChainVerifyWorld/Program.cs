// ChainVerifyWorld: independent verifier for the src/world primitive.
//
// Dumps the versions table through the sqlite3 CLI (used as a dumb row
// pipe, no chain logic there) and re-verifies the hash chain WITHOUT any
// Python code: an independent reimplementation of the chain rule, so a
// bug in src/world/core.py cannot vouch for itself.
//
// Chain rule (must match _row_hash / _genesis_prev_hash in core.py):
//   genesis_prev = SHA256-HEX( UTF8("world-genesis:{name}") )
//   row_hash     = SHA256-HEX( UTF8(
//                    prev_hash + LF + seq + LF + timestamp + LF +
//                    (actor or "") + LF + (note or "") + LF +
//                    status + LF + state) )
//   row 1 prev_hash must equal genesis_prev; every later row's
//   prev_hash must equal the previous row's hash.
//
// Usage: ChainVerifyWorld <path-to-world.db> <world-name>
// Exit code 0: chain valid (row count printed).
// Exit code 1: broken (first bad seq printed). Exit code 2: unusable input.

using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace ChainVerifyWorld;

public static class Program
{
    public static int Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.Error.WriteLine("usage: ChainVerifyWorld <world.db> <world-name>");
            return 2;
        }

        string dbPath = args[0];
        string worldName = args[1];
        if (!File.Exists(dbPath))
        {
            Console.Error.WriteLine("database not found: " + dbPath);
            return 2;
        }

        string json = DumpRows(dbPath);
        if (json == null)
        {
            return 2;
        }

        JsonDocument doc;
        try
        {
            doc = JsonDocument.Parse(json);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("cannot parse row dump: " + ex.Message);
            return 2;
        }

        string expectedPrev = Sha256Hex("world-genesis:" + worldName);
        long checkedRows = 0;
        long lastSeq = 0;

        foreach (JsonElement row in doc.RootElement.EnumerateArray())
        {
            long seq = row.GetProperty("seq").GetInt64();
            if (seq != lastSeq + 1)
            {
                Console.Error.WriteLine(
                    "seq gap at " + seq + " (expected " + (lastSeq + 1) + ")");
                return 1;
            }
            lastSeq = seq;

            string timestamp = Str(row, "timestamp");
            string actor = Str(row, "actor");
            string note = Str(row, "note");
            string status = Str(row, "status");
            string state = Str(row, "state");
            string prevHash = Str(row, "prev_hash");
            string storedHash = Str(row, "hash");

            if (prevHash != expectedPrev)
            {
                Console.Error.WriteLine(
                    "broken link at seq " + seq + ": prev_hash mismatch");
                return 1;
            }

            string payload = string.Join("\n", new string[]
            {
                prevHash, seq.ToString(), timestamp, actor, note, status, state
            });
            string recomputed = Sha256Hex(payload);
            if (!FixedTimeEqual(recomputed, storedHash))
            {
                Console.Error.WriteLine("hash mismatch at seq " + seq);
                return 1;
            }

            expectedPrev = storedHash;
            checkedRows++;
        }

        Console.WriteLine("OK: " + checkedRows + " rows verified");
        return 0;
    }

    private static string DumpRows(string dbPath)
    {
        // The sqlite3 CLI is a dumb row pipe here; it performs no chain
        // logic. --readonly keeps the verifier from modifying the DB.
        ProcessStartInfo psi = new ProcessStartInfo("sqlite3");
        psi.RedirectStandardOutput = true;
        psi.RedirectStandardError = true;
        psi.ArgumentList.Add("--json");
        psi.ArgumentList.Add("--readonly");
        psi.ArgumentList.Add(dbPath);
        psi.ArgumentList.Add(
            "SELECT seq, timestamp, actor, note, status, state,"
            + " prev_hash, hash FROM versions ORDER BY seq ASC;");
        using (Process proc = Process.Start(psi))
        {
            if (proc == null)
            {
                Console.Error.WriteLine("cannot start sqlite3");
                return null;
            }
            string json = proc.StandardOutput.ReadToEnd();
            string err = proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            if (proc.ExitCode != 0)
            {
                Console.Error.WriteLine("sqlite3 dump failed: " + err);
                return null;
            }
            return json;
        }
    }

    private static string Str(JsonElement row, string name)
    {
        JsonElement el;
        if (row.TryGetProperty(name, out el)
            && el.ValueKind == JsonValueKind.String)
        {
            string s = el.GetString();
            return s == null ? "" : s;
        }
        return "";
    }

    private static string Sha256Hex(string s)
    {
        byte[] bytes = SHA256.HashData(Encoding.UTF8.GetBytes(s));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }

    private static bool FixedTimeEqual(string a, string b)
    {
        return CryptographicOperations.FixedTimeEquals(
            Encoding.ASCII.GetBytes(a), Encoding.ASCII.GetBytes(b));
    }
}
