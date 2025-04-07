import os, pygame

def load_images(current_path, screen_width, screen_height):
    try:
        image_folder = os.path.join(current_path, "images")
        loaded_images = {}

        supported_formats = (".png", ".jpg")

        default_sizes = {
            "background.png": (screen_width, screen_height),
            "player.png": (64, 64),
            "bullet.png": (64, 64),
            "default": (32, 32)
        }

        def get_dynamic_size(filename):
            base_name = os.path.splitext(filename)[0].lower()
            if "large" in base_name:
                return (128, 128)
            elif "small" in base_name:
                return (16, 16)
            return default_sizes.get(filename, default_sizes["default"])

        for filename in os.listdir(image_folder):
            if filename.lower().endswith(supported_formats):
                image_path = os.path.join(image_folder, filename)
                image = pygame.image.load(image_path).convert_alpha()
                size = get_dynamic_size(filename)
                image = pygame.transform.scale(image, size)
                name = os.path.splitext(filename)[0]
                loaded_images[name] = image

        if "player" in loaded_images:
            loaded_images["player_original"] = loaded_images["player"].copy()
        if "bullet" in loaded_images:
            loaded_images["bullet_original"] = loaded_images["bullet"].copy()

        return loaded_images
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Image file not found: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load images: {e}")

if __name__ == "__main__":
    pygame.init()
    current_path = os.path.dirname(os.path.abspath(__file__))
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    images = load_images(current_path, screen_width, screen_height)
    print("Loaded images:", list(images.keys()))
    pygame.quit()