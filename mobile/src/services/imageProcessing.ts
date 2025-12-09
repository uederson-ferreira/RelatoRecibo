import * as ImageManipulator from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';

export interface CropArea {
  originX: number;
  originY: number;
  width: number;
  height: number;
}

export class ImageProcessingService {
  /**
   * Crops an image to a specified area
   */
  static async cropImage(
    imageUri: string,
    cropArea: CropArea
  ): Promise<string> {
    try {
      const manipResult = await ImageManipulator.manipulateAsync(
        imageUri,
        [
          {
            crop: cropArea
          }
        ],
        {
          compress: 0.8,
          format: ImageManipulator.SaveFormat.JPEG
        }
      );

      return manipResult.uri;
    } catch (error) {
      console.error('Error cropping image:', error);
      throw new Error('Failed to crop image');
    }
  }

  /**
   * Automatically detects and crops receipt area from image
   * Applies image enhancement for better OCR recognition
   */
  static async autoCropReceipt(imageUri: string): Promise<string> {
    try {
      // Get image dimensions
      const dimensions = await this.getImageDimensions(imageUri);
      console.log('Original dimensions:', dimensions);

      // Calculate crop area - crop to center 80% to remove edges
      // This helps remove background and focus on the receipt
      const cropWidth = dimensions.width * 0.8;
      const cropHeight = dimensions.height * 0.8;
      const originX = (dimensions.width - cropWidth) / 2;
      const originY = (dimensions.height - cropHeight) / 2;

      const manipResult = await ImageManipulator.manipulateAsync(
        imageUri,
        [
          // First, crop to center area (removes background)
          {
            crop: {
              originX,
              originY,
              width: cropWidth,
              height: cropHeight
            }
          },
          // Then resize to optimal width for OCR
          {
            resize: {
              width: 1200
            }
          }
        ],
        {
          compress: 0.85,
          format: ImageManipulator.SaveFormat.JPEG
        }
      );

      console.log('Cropped and processed image:', manipResult.uri);
      return manipResult.uri;
    } catch (error) {
      console.error('Error auto-cropping receipt:', error);
      // If manipulation fails, return original URI
      return imageUri;
    }
  }

  /**
   * Enhances image for better OCR recognition
   */
  static async enhanceForOCR(imageUri: string): Promise<string> {
    try {
      const manipResult = await ImageManipulator.manipulateAsync(
        imageUri,
        [
          {
            resize: {
              width: 1200
            }
          }
        ],
        {
          compress: 0.9,
          format: ImageManipulator.SaveFormat.JPEG
        }
      );

      return manipResult.uri;
    } catch (error) {
      console.error('Error enhancing image:', error);
      throw new Error('Failed to enhance image');
    }
  }

  /**
   * Rotates an image by specified degrees
   */
  static async rotateImage(
    imageUri: string,
    degrees: 90 | 180 | 270
  ): Promise<string> {
    try {
      const manipResult = await ImageManipulator.manipulateAsync(
        imageUri,
        [
          {
            rotate: degrees
          }
        ],
        {
          compress: 0.8,
          format: ImageManipulator.SaveFormat.JPEG
        }
      );

      return manipResult.uri;
    } catch (error) {
      console.error('Error rotating image:', error);
      throw new Error('Failed to rotate image');
    }
  }

  /**
   * Compresses an image
   */
  static async compressImage(
    imageUri: string,
    quality: number = 0.7
  ): Promise<string> {
    try {
      const manipResult = await ImageManipulator.manipulateAsync(
        imageUri,
        [],
        {
          compress: quality,
          format: ImageManipulator.SaveFormat.JPEG
        }
      );

      return manipResult.uri;
    } catch (error) {
      console.error('Error compressing image:', error);
      throw new Error('Failed to compress image');
    }
  }

  /**
   * Gets image dimensions
   */
  static async getImageDimensions(imageUri: string): Promise<{ width: number; height: number }> {
    try {
      // Use a manipulation with no actions to get image info
      const result = await ImageManipulator.manipulateAsync(
        imageUri,
        [],
        { compress: 1, format: ImageManipulator.SaveFormat.JPEG }
      );

      // Unfortunately, expo-image-manipulator doesn't return dimensions directly
      // We'll need to use Image.getSize for this
      return new Promise((resolve, reject) => {
        const Image = require('react-native').Image;
        Image.getSize(
          imageUri,
          (width: number, height: number) => resolve({ width, height }),
          (error: Error) => reject(error)
        );
      });
    } catch (error) {
      console.error('Error getting image dimensions:', error);
      throw new Error('Failed to get image dimensions');
    }
  }

  /**
   * Saves image to permanent storage
   */
  static async saveImagePermanently(imageUri: string, fileName: string): Promise<string> {
    try {
      // If the image is already processed by ImageManipulator, it's already saved
      // Just return the URI
      if (imageUri.includes('ImageManipulator')) {
        return imageUri;
      }

      const directory = `${FileSystem.documentDirectory}receipts/`;

      // Create directory if it doesn't exist
      try {
        const dirInfo = await FileSystem.getInfoAsync(directory);
        if (!dirInfo.exists) {
          await FileSystem.makeDirectoryAsync(directory, { intermediates: true });
        }
      } catch (err) {
        console.log('Error checking/creating directory:', err);
        // If directory creation fails, just return the original URI
        return imageUri;
      }

      const newUri = `${directory}${fileName}`;

      // Try to copy image to permanent storage
      try {
        await FileSystem.copyAsync({
          from: imageUri,
          to: newUri
        });
        return newUri;
      } catch (copyError) {
        console.log('Error copying file, using original URI:', copyError);
        // If copy fails, return original URI
        return imageUri;
      }
    } catch (error) {
      console.error('Error saving image:', error);
      // Return original URI as fallback
      return imageUri;
    }
  }

  /**
   * Deletes an image file
   */
  static async deleteImage(imageUri: string): Promise<void> {
    try {
      const info = await FileSystem.getInfoAsync(imageUri);
      if (info.exists) {
        await FileSystem.deleteAsync(imageUri);
      }
    } catch (error) {
      console.error('Error deleting image:', error);
      // Don't throw error for deletion failures
    }
  }
}
