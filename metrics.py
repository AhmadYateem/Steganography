"""
Image Quality Metrics Module

This module provides functions to calculate quality metrics for image steganography:
- MSE (Mean Squared Error): Average squared pixel differences
- PSNR (Peak Signal-to-Noise Ratio): Quality in decibels
- SSIM (Structural Similarity Index): Perceptual similarity

These metrics help evaluate how imperceptible the steganography is.
"""

import numpy as np
from typing import Tuple


def load_image_for_metrics(image_path: str):
    """
    Load an image as numpy array for metrics calculation.

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (pixel_array, format)
    """
    # Import here to avoid circular dependency
    from image_stego import load_image
    return load_image(image_path)


def calculate_mse(original_path: str, stego_path: str) -> float:
    """
    Calculate MSE (Mean Squared Error) between two images.

    MSE measures the average squared difference between corresponding pixels.
    Lower MSE = better quality (less change)

    Formula:
        MSE = (1 / total_pixels) × Σ(original - stego)²

    Args:
        original_path: Path to original image
        stego_path: Path to stego image

    Returns:
        MSE value (lower is better)
        - MSE = 0: Perfect (images identical)
        - MSE < 1: Excellent (imperceptible differences)
        - MSE < 10: Good (very minor differences)
        - MSE > 100: Poor (visible differences)

    Example:
        >>> mse = calculate_mse("original.png", "stego.png")
        >>> print(f"MSE: {mse:.4f}")
        MSE: 0.3251
    """
    # Load both images
    orig_pixels, _ = load_image_for_metrics(original_path)
    stego_pixels, _ = load_image_for_metrics(stego_path)

    # Convert to float for accurate calculation
    orig_float = orig_pixels.astype(float)
    stego_float = stego_pixels.astype(float)

    # Calculate squared differences
    squared_diff = (orig_float - stego_float) ** 2

    # Calculate mean (average) of all squared differences
    mse = np.mean(squared_diff)

    return float(mse)


def calculate_psnr(original_path: str, stego_path: str, max_pixel_value: int = 255) -> float:
    """
    Calculate PSNR (Peak Signal-to-Noise Ratio) between two images.

    PSNR measures image quality in decibels (dB).
    Higher PSNR = better quality (less distortion)

    Formula:
        PSNR = 10 × log₁₀(MAX² / MSE)

    where MAX = maximum possible pixel value (usually 255)

    Args:
        original_path: Path to original image
        stego_path: Path to stego image
        max_pixel_value: Maximum pixel value (default 255 for 8-bit images)

    Returns:
        PSNR value in dB (higher is better)
        - PSNR > 50 dB: Excellent (imperceptible differences)
        - PSNR 40-50 dB: Very good (nearly imperceptible)
        - PSNR 30-40 dB: Acceptable
        - PSNR < 30 dB: Poor (visible differences)

    Example:
        >>> psnr = calculate_psnr("original.png", "stego.png")
        >>> print(f"PSNR: {psnr:.2f} dB")
        PSNR: 52.15 dB
    """
    # Calculate MSE first
    mse = calculate_mse(original_path, stego_path)

    # Handle perfect match (MSE = 0)
    if mse == 0:
        return float('inf')  # Infinite PSNR (perfect quality)

    # Calculate PSNR using the formula
    # PSNR = 10 × log₁₀(MAX² / MSE)
    max_squared = max_pixel_value ** 2
    psnr = 10 * np.log10(max_squared / mse)

    return float(psnr)


def calculate_ssim(original_path: str, stego_path: str) -> float:
    """
    Calculate SSIM (Structural Similarity Index) between two images.

    SSIM measures perceived image quality by comparing:
    - Luminance (brightness)
    - Contrast
    - Structure

    This correlates better with human perception than MSE/PSNR.

    Args:
        original_path: Path to original image
        stego_path: Path to stego image

    Returns:
        SSIM value between -1 and 1 (higher is better)
        - SSIM = 1.0: Images are identical
        - SSIM > 0.99: Excellent (imperceptible)
        - SSIM > 0.95: Very good
        - SSIM > 0.90: Good
        - SSIM < 0.90: Poor

    Example:
        >>> ssim = calculate_ssim("original.png", "stego.png")
        >>> print(f"SSIM: {ssim:.4f}")
        SSIM: 0.9987

    Note:
        Uses scikit-image's SSIM implementation for accuracy.
        If not available, falls back to simple correlation-based measure.
    """
    # Load both images
    orig_pixels, _ = load_image_for_metrics(original_path)
    stego_pixels, _ = load_image_for_metrics(stego_path)

    # Try to use scikit-image's SSIM (most accurate)
    try:
        from skimage.metrics import structural_similarity as ssim
        # Calculate SSIM for multichannel (RGB) images
        ssim_value = ssim(orig_pixels, stego_pixels,
                         channel_axis=2,  # RGB channels
                         data_range=255)  # 8-bit images
        return float(ssim_value)

    except ImportError:
        # Fallback: Simple correlation-based similarity
        # This is a simplified version but still useful

        # Convert to float and normalize
        orig_norm = orig_pixels.astype(float) / 255.0
        stego_norm = stego_pixels.astype(float) / 255.0

        # Calculate means
        mean_orig = np.mean(orig_norm)
        mean_stego = np.mean(stego_norm)

        # Calculate variances
        var_orig = np.var(orig_norm)
        var_stego = np.var(stego_norm)

        # Calculate covariance
        covar = np.mean((orig_norm - mean_orig) * (stego_norm - mean_stego))

        # Constants for stability (from SSIM paper)
        C1 = (0.01 * 1.0) ** 2  # For luminance
        C2 = (0.03 * 1.0) ** 2  # For contrast

        # SSIM formula (simplified single-value version)
        numerator = (2 * mean_orig * mean_stego + C1) * (2 * covar + C2)
        denominator = (mean_orig**2 + mean_stego**2 + C1) * (var_orig + var_stego + C2)

        ssim_value = numerator / denominator

        return float(ssim_value)


def calculate_metrics_summary(original_path: str, stego_path: str) -> dict:
    """
    Calculate all quality metrics and return a comprehensive summary.

    This is the main function you should use to evaluate stego image quality!

    Args:
        original_path: Path to original cover image
        stego_path: Path to stego image

    Returns:
        Dictionary with all metrics and quality assessment:
        {
            'mse': 0.3251,
            'psnr': 52.15,
            'ssim': 0.9987,
            'quality_assessment': 'Excellent',
            'imperceptible': True,
            'details': {
                'mse_interpretation': '...',
                'psnr_interpretation': '...',
                'ssim_interpretation': '...'
            },
            'recommendations': [...]
        }

    Example:
        >>> metrics = calculate_metrics_summary("original.png", "stego.png")
        >>> print(f"Quality: {metrics['quality_assessment']}")
        >>> print(f"PSNR: {metrics['psnr']:.2f} dB")
        >>> print(f"SSIM: {metrics['ssim']:.4f}")
    """
    # Calculate all three metrics
    mse = calculate_mse(original_path, stego_path)
    psnr = calculate_psnr(original_path, stego_path)
    ssim = calculate_ssim(original_path, stego_path)

    # Interpret MSE
    if mse == 0:
        mse_interp = "Perfect (images identical)"
    elif mse < 1:
        mse_interp = "Excellent (imperceptible differences)"
    elif mse < 10:
        mse_interp = "Good (very minor differences)"
    elif mse < 100:
        mse_interp = "Acceptable (minor differences)"
    else:
        mse_interp = "Poor (visible differences)"

    # Interpret PSNR
    if psnr == float('inf'):
        psnr_interp = "Perfect (images identical)"
    elif psnr > 50:
        psnr_interp = "Excellent (imperceptible)"
    elif psnr > 40:
        psnr_interp = "Very good (nearly imperceptible)"
    elif psnr > 30:
        psnr_interp = "Acceptable"
    else:
        psnr_interp = "Poor (visible distortion)"

    # Interpret SSIM
    if ssim >= 0.999:
        ssim_interp = "Excellent (imperceptible)"
    elif ssim >= 0.99:
        ssim_interp = "Very good (nearly imperceptible)"
    elif ssim >= 0.95:
        ssim_interp = "Good"
    elif ssim >= 0.90:
        ssim_interp = "Acceptable"
    else:
        ssim_interp = "Poor"

    # Overall quality assessment (based on all metrics)
    if psnr > 50 and ssim >= 0.99:
        overall = "Excellent"
        imperceptible = True
    elif psnr > 40 and ssim >= 0.95:
        overall = "Very Good"
        imperceptible = True
    elif psnr > 30 and ssim >= 0.90:
        overall = "Good"
        imperceptible = False
    else:
        overall = "Poor"
        imperceptible = False

    return {
        # Raw metric values
        'mse': round(mse, 4),
        'psnr': round(psnr, 2) if psnr != float('inf') else 'Inf',
        'ssim': round(ssim, 4),

        # Overall assessment
        'quality_assessment': overall,
        'imperceptible': imperceptible,

        # Detailed interpretations
        'details': {
            'mse_interpretation': mse_interp,
            'psnr_interpretation': psnr_interp,
            'ssim_interpretation': ssim_interp
        },

        # Recommendations
        'recommendations': get_quality_recommendations(mse, psnr, ssim)
    }


def get_quality_recommendations(mse: float, psnr: float, ssim: float) -> list:
    """
    Get recommendations based on quality metrics.

    Args:
        mse: Mean Squared Error
        psnr: Peak Signal-to-Noise Ratio
        ssim: Structural Similarity Index

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if psnr < 40:
        recommendations.append("Consider using fewer bits per pixel (e.g., 1 instead of 2 or 3)")

    if ssim < 0.95:
        recommendations.append("Image quality is reduced - steganography may be detectable")

    if mse > 10:
        recommendations.append("High MSE indicates significant changes - use a different cover image")

    if psnr > 50 and ssim > 0.99:
        recommendations.append("Excellent quality! Changes are imperceptible.")

    if not recommendations:
        recommendations.append("Quality is acceptable for steganography use")

    return recommendations


def print_metrics_report(metrics: dict, show_details: bool = True) -> None:
    """
    Print a formatted report of quality metrics.

    Args:
        metrics: Dictionary from calculate_metrics_summary()
        show_details: Whether to show detailed interpretations

    Example:
        >>> metrics = calculate_metrics_summary("original.png", "stego.png")
        >>> print_metrics_report(metrics)
    """
    print("\n" + "=" * 60)
    print("  IMAGE QUALITY METRICS REPORT")
    print("=" * 60)

    print(f"\n{'Metric':<20} {'Value':<15} {'Assessment'}")
    print("-" * 60)

    # MSE
    print(f"{'MSE':<20} {metrics['mse']:<15} ", end="")
    if show_details:
        print(metrics['details']['mse_interpretation'])
    else:
        print()

    # PSNR
    psnr_str = f"{metrics['psnr']} dB" if metrics['psnr'] != 'Inf' else "Infinite"
    print(f"{'PSNR':<20} {psnr_str:<15} ", end="")
    if show_details:
        print(metrics['details']['psnr_interpretation'])
    else:
        print()

    # SSIM
    print(f"{'SSIM':<20} {metrics['ssim']:<15} ", end="")
    if show_details:
        print(metrics['details']['ssim_interpretation'])
    else:
        print()

    print("-" * 60)
    print(f"\n{'Overall Quality:':<20} {metrics['quality_assessment']}")
    print(f"{'Imperceptible:':<20} {'Yes' if metrics['imperceptible'] else 'No'}")

    if metrics['recommendations']:
        print(f"\n{'Recommendations:':}")
        for i, rec in enumerate(metrics['recommendations'], 1):
            print(f"  {i}. {rec}")

    print("=" * 60 + "\n")
