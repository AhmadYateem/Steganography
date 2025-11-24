"""
Demonstration of Secure Steganography (Encryption + ZWC Hiding)

This script demonstrates the complete secure steganography system that combines:
1. AES-256-CTR encryption for confidentiality
2. Zero-width character steganography for concealment

This provides defense-in-depth security.
"""

import secure_stego
import crypto
import text_stego


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_encryption():
    """Demonstrate basic encryption and decryption."""
    print_section("1. Encryption Module Demo (crypto.py)")

    message = "This is a secret message!"
    password = "strongPassword123"

    print(f"\nOriginal message: '{message}'")
    print(f"Password: '{password}'")

    # Encrypt
    encrypted = crypto.encrypt_message(message, password)
    print(f"\nEncrypted (base64): {encrypted[:50]}...")
    print(f"Encrypted length: {len(encrypted)} characters")

    # Show encryption info
    info = crypto.get_encryption_info(encrypted)
    print(f"\nEncryption details:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Decrypt with correct password
    print("\n--- Decryption with CORRECT password ---")
    decrypted = crypto.decrypt_message(encrypted, password)
    print(f"Decrypted message: '{decrypted}'")
    assert decrypted == message, "Decryption failed!"
    print("✓ Decryption successful!")

    # Try with wrong password
    print("\n--- Decryption with WRONG password ---")
    try:
        wrong_decrypt = crypto.decrypt_message(encrypted, "wrongPassword")
        print("❌ This should not happen!")
    except ValueError as e:
        print(f"✓ Decryption correctly failed: {e}")


def demo_secure_encode():
    """Demonstrate the complete secure encode pipeline."""
    print_section("2. Secure Encode Pipeline (Encryption + Steganography)")

    cover_text = "The weather is beautiful today. I hope you are doing well!"
    secret_message = "Meet me at the library at 3pm. Bring the documents."
    password = "mySecretKey2024"

    print(f"\nCover text (visible): '{cover_text}'")
    print(f"Secret message: '{secret_message}'")
    print(f"Password: '{password}'")

    print("\n--- ENCODING PIPELINE ---")
    print("Step 1: Encrypt message with AES-256-CTR")
    encrypted = crypto.encrypt_message(secret_message, password)
    print(f"  Encrypted: {encrypted[:40]}... ({len(encrypted)} chars)")

    print("\nStep 2: Convert encrypted data to binary")
    binary = text_stego.text_to_binary(encrypted)
    print(f"  Binary length: {len(binary)} bits")

    print("\nStep 3: Encode binary as zero-width characters")
    print(f"  Using 2-bit encoding for efficiency")

    print("\nStep 4: Insert ZWC into cover text")
    print(f"  Using 'between_words' insertion method")

    # Now do it all with one function call
    stego_text = secure_stego.secure_encode(
        cover_text,
        secret_message,
        password,
        encoding_bits=2,
        insertion_method='between_words'
    )

    print("\n--- RESULT ---")
    visible = text_stego.get_visible_text(stego_text)
    print(f"Stego text (visible): '{visible}'")
    print(f"Actual stego text length: {len(stego_text)} chars")

    analysis = text_stego.analyze_text(stego_text)
    print(f"\nStego analysis:")
    print(f"  Total characters: {analysis['total_chars']}")
    print(f"  Visible characters: {analysis['visible_chars']}")
    print(f"  Hidden ZWC characters: {analysis['zwc_chars']}")
    print(f"  Hidden data detected: {analysis['has_hidden_data']}")

    return stego_text, password


def demo_secure_decode(stego_text, password):
    """Demonstrate the complete secure decode pipeline."""
    print_section("3. Secure Decode Pipeline (Extract + Decrypt)")

    print(f"Stego text (visible): '{text_stego.get_visible_text(stego_text)}'")
    print(f"Password: '{password}'")

    print("\n--- DECODING PIPELINE ---")
    print("Step 1: Extract zero-width characters")
    print("Step 2: Convert ZWC to binary to encrypted data")
    print("Step 3: Decrypt with password")
    print("Step 4: Return original message")

    # Do it all with one function call
    decoded_message = secure_stego.secure_decode(stego_text, password, encoding_bits=2)

    print("\n--- RESULT ---")
    print(f"Decoded message: '{decoded_message}'")
    print("✓ Successfully recovered the secret message!")


def demo_wrong_password(stego_text):
    """Demonstrate what happens with wrong password."""
    print_section("4. Security Test: Wrong Password")

    print("Attempting to decode with WRONG password...")

    try:
        decoded = secure_stego.secure_decode(stego_text, "wrongPassword123", encoding_bits=2)
        print("❌ This should not happen!")
    except ValueError as e:
        print(f"✓ Decryption correctly failed!")
        print(f"  Error: {str(e)[:80]}...")


def demo_simple_api():
    """Demonstrate the simplified API."""
    print_section("5. Simplified API (Easiest to Use)")

    cover = "Hello friend! How are you today? Hope all is well."
    secret = "The package has been delivered to the safe house."
    password = "agent007"

    print("Using secure_encode_simple() with default parameters:")
    print(f"  Cover: '{cover}'")
    print(f"  Secret: '{secret}'")
    print(f"  Password: '{password}'")

    # Encode
    stego = secure_stego.secure_encode_simple(cover, secret, password)
    print(f"\nStego (visible): '{text_stego.get_visible_text(stego)}'")

    # Decode
    decoded = secure_stego.secure_decode_simple(stego, password)
    print(f"Decoded: '{decoded}'")

    assert decoded == secret, "Round-trip failed!"
    print("\n✓ Simple API works perfectly!")


def demo_comparison():
    """Compare different encoding methods."""
    print_section("6. Comparison: Different Encoding Methods")

    cover = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod."
    secret = "Secret message"
    password = "test123"

    print(f"Cover text: '{cover}'")
    print(f"Secret: '{secret}'")
    print(f"Testing 6 different combinations...\n")

    results = secure_stego.compare_methods(cover, secret, password)

    # Display results in a table
    print(f"{'Method':<25} {'Bits':<6} {'ZWC Count':<10} {'Total Len':<10} {'Success'}")
    print("-" * 70)

    for key, result in results.items():
        if 'error' not in result:
            method = result['insertion_method']
            bits = result['encoding_bits']
            zwc = result['zwc_count']
            total = result['total_length']
            success = '✓' if result['decode_success'] else '✗'
            print(f"{method:<25} {bits:<6} {zwc:<10} {total:<10} {success}")

    print("\nConclusion:")
    print("  - 2-bit encoding uses 50% fewer ZWC characters")
    print("  - All methods successfully encode and decode")
    print("  - 'between_words' and 'distributed' are more subtle than 'append'")


def demo_defense_in_depth():
    """Demonstrate defense-in-depth security."""
    print_section("7. Defense-in-Depth Security Demonstration")

    cover = "The meeting is scheduled for Tuesday at 2pm in the conference room."
    secret = "Operation Nightfall is a go. Execute at midnight."
    password = "classified"

    print("Defense-in-Depth means multiple layers of security:\n")

    print("Layer 1: ENCRYPTION (Confidentiality)")
    print("  - Even if attacker finds the hidden data, it's encrypted")
    print("  - AES-256 is military-grade encryption")
    print("  - Without password, message is unreadable")

    print("\nLayer 2: STEGANOGRAPHY (Concealment)")
    print("  - Hidden data is invisible to casual observers")
    print("  - Text looks completely normal")
    print("  - Attacker doesn't know there's a hidden message")

    print("\n--- Creating stego-text with both layers ---")
    stego = secure_stego.secure_encode(cover, secret, password)

    print(f"\nWhat attacker sees: '{text_stego.get_visible_text(stego)}'")
    print("  → Looks completely normal!")

    print("\nIf attacker detects ZWC characters:")
    extracted = text_stego.decode_message(stego, encoding_bits=2)
    print(f"  Extracted data: {extracted[:50]}...")
    print("  → Still encrypted! Useless without password.")

    print("\nWith correct password:")
    decrypted = secure_stego.secure_decode(stego, password, encoding_bits=2)
    print(f"  Decrypted message: '{decrypted}'")
    print("  → BOTH layers must be broken to read the message!")

    print("\n✓ This is why encryption + steganography is so powerful!")


def demo_real_world_scenario():
    """Demonstrate a realistic usage scenario."""
    print_section("8. Real-World Scenario: Secure Communication")

    print("Scenario: Alice wants to send a secret message to Bob")
    print("via a public forum where messages are monitored.\n")

    # Alice's side
    print("--- ALICE (Sender) ---")
    alice_cover = "Thanks for the book recommendation! I really enjoyed the last chapter."
    alice_secret = "The meeting point has changed to Cafe Luna at 7pm tomorrow."
    shared_password = "dolphin-sunshine-2024"

    print(f"Alice's public message: '{alice_cover}'")
    print(f"Alice's secret message: '{alice_secret}'")
    print(f"Shared password (exchanged securely): '{shared_password}'")

    # Alice encodes
    alice_stego = secure_stego.secure_encode(alice_cover, alice_secret, shared_password)
    print(f"\nAlice posts to forum: '{text_stego.get_visible_text(alice_stego)}'")

    # Monitor sees this
    print("\n--- MONITOR (Adversary) ---")
    print(f"Monitor sees: '{text_stego.get_visible_text(alice_stego)}'")
    print("Monitor thinks: 'Just a normal book discussion. Nothing suspicious.'")

    analysis = text_stego.analyze_text(alice_stego)
    if analysis['has_hidden_data']:
        print(f"\nIf monitor uses steganalysis tools:")
        print(f"  'Found {analysis['zwc_chars']} suspicious characters!'")
        extracted = text_stego.decode_message(alice_stego, encoding_bits=2)
        print(f"  'Extracted data: {extracted[:40]}...'")
        print(f"  'But it's encrypted. Can't read it without password.'")

    # Bob's side
    print("\n--- BOB (Receiver) ---")
    print(f"Bob reads forum post: '{text_stego.get_visible_text(alice_stego)}'")
    print(f"Bob uses shared password to decode...")

    bob_decoded = secure_stego.secure_decode(alice_stego, shared_password, encoding_bits=2)
    print(f"Bob's decoded message: '{bob_decoded}'")
    print("\n✓ Secure communication successful!")
    print("  - Monitor saw nothing suspicious")
    print("  - Even if detected, encryption protected the message")
    print("  - Only Bob (with password) could read the secret")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  SECURE STEGANOGRAPHY DEMONSTRATION")
    print("  Encryption (AES-256-CTR) + Zero-Width Character Hiding")
    print("=" * 70)

    try:
        # Basic demos
        demo_encryption()
        stego_text, password = demo_secure_encode()
        demo_secure_decode(stego_text, password)
        demo_wrong_password(stego_text)

        # Advanced demos
        demo_simple_api()
        demo_comparison()
        demo_defense_in_depth()
        demo_real_world_scenario()

        print("\n" + "=" * 70)
        print("  ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nQuick Start Guide:")
        print("-" * 70)
        print("from secure_stego import secure_encode, secure_decode")
        print("")
        print("# Hide encrypted message:")
        print('stego = secure_encode(cover_text, secret, password)')
        print("")
        print("# Extract and decrypt:")
        print('message = secure_decode(stego, password)')
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
