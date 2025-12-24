import base64
import struct
import zlib

def create_png(size, color=(10, 132, 255)):
    """Create a simple PNG icon"""
    
    def png_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
        return chunk_len + chunk_type + data + chunk_crc
    
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    ihdr = png_chunk(b'IHDR', ihdr_data)
    
    # Image data - solid color with rounded corners effect
    raw_data = b''
    for y in range(size):
        raw_data += b'\x00'  # Filter type: None
        for x in range(size):
            # Simple rounded corner check
            corner_radius = size // 4
            in_corner = False
            
            # Check corners
            corners = [
                (corner_radius, corner_radius),
                (size - corner_radius - 1, corner_radius),
                (corner_radius, size - corner_radius - 1),
                (size - corner_radius - 1, size - corner_radius - 1)
            ]
            
            for cx, cy in corners:
                dx = abs(x - cx)
                dy = abs(y - cy)
                if (x < corner_radius or x >= size - corner_radius) and \
                   (y < corner_radius or y >= size - corner_radius):
                    if dx * dx + dy * dy > corner_radius * corner_radius:
                        in_corner = True
                        break
            
            if in_corner:
                raw_data += bytes([13, 13, 15])  # Dark background
            else:
                raw_data += bytes(color)
    
    idat_data = zlib.compress(raw_data, 9)
    idat = png_chunk(b'IDAT', idat_data)
    
    # IEND chunk
    iend = png_chunk(b'IEND', b'')
    
    return signature + ihdr + idat + iend

# Create icons
for size in [16, 48, 128]:
    png_data = create_png(size)
    with open(f'icon{size}.png', 'wb') as f:
        f.write(png_data)
    print(f'Created icon{size}.png')

print('Done!')
