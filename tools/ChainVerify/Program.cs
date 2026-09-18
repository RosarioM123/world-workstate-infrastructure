// ChainVerify — independent WORLD ledger verifier.
//
// Reads a ledger JSON export (see tools/export_ledger.py) and re-verifies
// the SHA-256 hash chain WITHOUT using any of the Python code: an
// independent reimplementation of the chain rule, so a bug in engine.py
// cannot vouch for itself.
//
// Chain rule (must match engine._hash_record exactly):
//   record_hash == SHA256-HEX( UTF8(
//     timestamp + "|" + entity_id + "|" + action + "|" +
//     payload + "|" + (previous_hash ?? "GENESIS") + "|" + status ) )
// and each row's previous_hash must equal the preceding row's record_hash
// (null for the genesis row).
//
// Exit code 0: chain valid. Exit code 1: broken (first bad id printed)
// or unusable input.

using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

if (args.Length != 1)
{
    Console.Error.WriteLine("usage: ChainVerify <ledger.json>");
    return 2;
}

JsonDocument doc;
try
{
    doc = JsonDocument.Parse(File.ReadAllText(args[0]));
}
catch (Exception ex)
{
    Console.Error.WriteLine($"cannot read ledger export: {ex.Message}");
    return 2;
}

var rows = doc.RootElement.EnumerateArray()
    .OrderBy(e => e.GetProperty("transaction_id").GetInt64())
    .ToList();

string? expectedPrevious = null;
foreach (var row in rows)
{
    long txId = row.GetProperty("transaction_id").GetInt64();
    string timestamp = row.GetProperty("timestamp").GetString() ?? "";
    string entityId = row.GetProperty("entity_id").GetString() ?? "";
    string action = row.GetProperty("action").GetString() ?? "";
    string payload = row.GetProperty("payload").GetString() ?? "";
    string status = row.GetProperty("status").GetString() ?? "";

    string previousHash;
    var prevProp = row.GetProperty("previous_hash");
    if (prevProp.ValueKind == JsonValueKind.Null)
        previousHash = "GENESIS";
    else
        previousHash = prevProp.GetString() ?? "";

    string storedPrevious = prevProp.ValueKind == JsonValueKind.Null
        ? null!
        : prevProp.GetString()!;
    if (storedPrevious != expectedPrevious)
    {
        Console.WriteLine($"BROKEN previous_hash link at transaction {txId}");
        return 1;
    }

    string material = string.Join("|",
        timestamp, entityId, action, payload, previousHash, status);
    byte[] digest = SHA256.HashData(Encoding.UTF8.GetBytes(material));
    string recomputed = Convert.ToHexString(digest).ToLowerInvariant();

    string recordHash = row.GetProperty("record_hash").GetString() ?? "";
    if (!CryptographicOperations.FixedTimeEquals(
            Encoding.ASCII.GetBytes(recomputed),
            Encoding.ASCII.GetBytes(recordHash)))
    {
        Console.WriteLine($"BROKEN record_hash at transaction {txId}");
        return 1;
    }

    expectedPrevious = recordHash;
}

Console.WriteLine($"OK: {rows.Count} records verified, chain intact.");
return 0;
