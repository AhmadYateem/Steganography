"""
Demonstration of Zero-Width Character (ZWC) Text Steganography

This script demonstrates the core functionality of the text steganography module.
"""

import text_stego


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_text_to_binary():
    """Demonstrate text to binary conversion."""
    print_section("1. Text to Binary Conversion")

    test_messages = ["Hi", "A", "Secret"]

    for message in test_messages:
        binary = text_stego.text_to_binary(message)
        print(f"\nText:   '{message}'")
        print(f"Binary: {binary}")
        print(f"Length: {len(binary)} bits ({len(binary)//8} bytes)")

        # Verify round-trip conversion
        decoded = text_stego.binary_to_text(binary)
        print(f"Decoded back: '{decoded}'")
        assert decoded == message, "Round-trip conversion failed!"


def demo_binary_to_zwc():
    """Demonstrate binary to zero-width character mapping."""
    print_section("2. Binary to Zero-Width Character Mapping")

    binary = "01101000"  # Letter 'h'

    print("\n1-bit encoding (2 ZWC characters for 0 and 1):")
    zwc_1bit = text_stego.binary_to_zwc(binary, encoding_bits=1)
    print(f"Binary:  {binary}")
    print(f"ZWC:     {repr(zwc_1bit)}")
    print(f"Length:  {len(zwc_1bit)} characters")

    # Show the Unicode code points
    unicode_points = [f"U+{ord(c):04X}" for c in zwc_1bit]
    print(f"Unicode: {' '.join(unicode_points)}")

    print("\n2-bit encoding (4 ZWC characters for 00, 01, 10, 11):")
    zwc_2bit = text_stego.binary_to_zwc(binary, encoding_bits=2)
    print(f"Binary:  {binary}")
    print(f"ZWC:     {repr(zwc_2bit)}")
    print(f"Length:  {len(zwc_2bit)} characters (50% reduction)")

    # Show the Unicode code points
    unicode_points = [f"U+{ord(c):04X}" for c in zwc_2bit]
    print(f"Unicode: {' '.join(unicode_points)}")

    # Verify round-trip conversion
    binary_back_1 = text_stego.zwc_to_binary(zwc_1bit, encoding_bits=1)
    binary_back_2 = text_stego.zwc_to_binary(zwc_2bit, encoding_bits=2)
    assert binary_back_1 == binary, "1-bit round-trip failed!"
    assert binary_back_2 == binary or binary_back_2 == binary + '0', "2-bit round-trip failed!"
    print("\n✓ Round-trip conversion successful!")


def demo_encode_message():
    """Demonstrate hiding messages in cover text."""
    print_section("3. Hiding Messages in Cover Text")

    cover_text = "The quick brown fox jumps over the lazy dog."
    secret_message = "Secret"

    print(f"\nCover text:     '{cover_text}'")
    print(f"Secret message: '{secret_message}'")

    # Method 1: Append (1-bit encoding)
    print("\n--- Method 1: Append with 1-bit encoding ---")
    stego_1 = text_stego.encode_message(
        cover_text, secret_message,
        encoding_bits=1,
        insertion_method='append'
    )
    print(f"Stego text looks like: '{text_stego.get_visible_text(stego_1)}'")
    print(f"Actual stego text length: {len(stego_1)} chars")
    print(f"Visible text length:      {len(cover_text)} chars")
    print(f"Hidden data:              {len(stego_1) - len(cover_text)} ZWC chars")

    # Verify decoding
    decoded_1 = text_stego.decode_message(stego_1, encoding_bits=1)
    print(f"Decoded message: '{decoded_1}'")
    assert decoded_1 == secret_message, "Decoding failed!"
    print("✓ Encoding and decoding successful!")

    # Method 2: Between words (2-bit encoding)
    print("\n--- Method 2: Between words with 2-bit encoding ---")
    stego_2 = text_stego.encode_message(
        cover_text, secret_message,
        encoding_bits=2,
        insertion_method='between_words'
    )
    print(f"Stego text looks like: '{text_stego.get_visible_text(stego_2)}'")

    decoded_2 = text_stego.decode_message(stego_2, encoding_bits=2)
    print(f"Decoded message: '{decoded_2}'")
    assert decoded_2 == secret_message, "Decoding failed!"
    print("✓ Encoding and decoding successful!")

    # Method 3: Distributed
    print("\n--- Method 3: Distributed with 1-bit encoding ---")
    stego_3 = text_stego.encode_message(
        cover_text, secret_message,
        encoding_bits=1,
        insertion_method='distributed'
    )
    print(f"Stego text looks like: '{text_stego.get_visible_text(stego_3)}'")

    decoded_3 = text_stego.decode_message(stego_3, encoding_bits=1)
    print(f"Decoded message: '{decoded_3}'")
    assert decoded_3 == secret_message, "Decoding failed!"
    print("✓ Encoding and decoding successful!")


def demo_analysis():
    """Demonstrate text analysis for ZWC detection."""
    print_section("4. Text Analysis and ZWC Detection")

    # Normal text
    normal_text = "This is normal text without any hidden data."
    print(f"\nAnalyzing: '{normal_text}'")
    analysis = text_stego.analyze_text(normal_text)
    print(f"Results: {analysis}")

    # Stego text
    cover = "Hello, world!"
    secret = "Hi"
    stego = text_stego.encode_message(cover, secret, encoding_bits=1)

    print(f"\nAnalyzing stego text that looks like: '{text_stego.get_visible_text(stego)}'")
    analysis = text_stego.analyze_text(stego)
    print(f"Results: {analysis}")

    if analysis['has_hidden_data']:
        print("\n⚠️  Hidden data detected!")
        print(f"   - Total characters: {analysis['total_chars']}")
        print(f"   - Visible characters: {analysis['visible_chars']}")
        print(f"   - Hidden ZWC characters: {analysis['zwc_chars']}")
        print(f"   - ZWC breakdown: {analysis['zwc_breakdown']}")


def demo_comparison():
    """Compare 1-bit vs 2-bit encoding."""
    print_section("5. Comparison: 1-bit vs 2-bit Encoding")

    secret_message = "This is a longer secret message for comparison!"
    cover_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    print(f"\nSecret message: '{secret_message}'")
    print(f"Message length: {len(secret_message)} characters")

    # 1-bit encoding
    binary = text_stego.text_to_binary(secret_message)
    zwc_1bit = text_stego.binary_to_zwc(binary, encoding_bits=1)
    stego_1bit = text_stego.encode_message(cover_text, secret_message, encoding_bits=1)

    print(f"\n1-bit encoding:")
    print(f"  Binary length:  {len(binary)} bits")
    print(f"  ZWC count:      {len(zwc_1bit)} characters")
    print(f"  Stego length:   {len(stego_1bit)} chars total")
    print(f"  Overhead:       {len(stego_1bit) - len(cover_text)} chars")

    # 2-bit encoding
    zwc_2bit = text_stego.binary_to_zwc(binary, encoding_bits=2)
    stego_2bit = text_stego.encode_message(cover_text, secret_message, encoding_bits=2)

    print(f"\n2-bit encoding:")
    print(f"  Binary length:  {len(binary)} bits")
    print(f"  ZWC count:      {len(zwc_2bit)} characters")
    print(f"  Stego length:   {len(stego_2bit)} chars total")
    print(f"  Overhead:       {len(stego_2bit) - len(cover_text)} chars")

    reduction = (1 - len(zwc_2bit) / len(zwc_1bit)) * 100
    print(f"\n2-bit encoding reduces ZWC count by ~{reduction:.1f}%")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  ZERO-WIDTH CHARACTER (ZWC) TEXT STEGANOGRAPHY DEMO")
    print("=" * 70)

    try:
        demo_text_to_binary()
        demo_binary_to_zwc()
        demo_encode_message()
        demo_analysis()
        demo_comparison()

        print("\n" + "=" * 70)
        print("  ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
