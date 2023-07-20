import sys
import os
from ctypes import *
from ctypes.util import find_library
import enum

def load_libairspy():
    if sys.platform == "linux" and 'LD_LIBRARY_PATH' in os.environ.keys():
        ld_library_paths = [local_path for local_path in os.environ['LD_LIBRARY_PATH'].split(':') if local_path.strip()]
        if "AIRSPY_TEST_PATH" in os.environ:
            ld_library_paths = [os.environ["AIRSPY_TEST_PATH"]]
        driver_files = [local_path + '/libairspy.so' for local_path in ld_library_paths]
    else:
        driver_files = []
    driver_files += ['libairspy.so']
    driver_files += ['airspy.dll', 'libairspy.so', 'libairspy.dylib','/usr/local/lib/libairspy.so']
    driver_files += ['..//airspy.dll', '..//libairspy.so']
    driver_files += [lambda : find_library('airspy'), lambda : find_library('libairspy')]
    dll = None

    for driver in driver_files:
        if callable(driver):
            driver = driver()
        if driver is None:
            continue
        #print("Search for driver named %s"%(driver))
        try:
            dll = CDLL(driver)
            break
        except:
            pass
    else:
        raise ImportError('Error loading libairspy. Make sure libairspy '\
                          '(and all of its dependencies) are in your path')

    return dll

libairspy = load_libairspy()


#enum airspy_sample_type
#{
#	AIRSPY_SAMPLE_FLOAT32_IQ = 0,   /* 2 * 32bit float per sample */
#	AIRSPY_SAMPLE_FLOAT32_REAL = 1, /* 1 * 32bit float per sample */
#	AIRSPY_SAMPLE_INT16_IQ = 2,     /* 2 * 16bit int per sample */
#	AIRSPY_SAMPLE_INT16_REAL = 3,   /* 1 * 16bit int per sample */
#	AIRSPY_SAMPLE_UINT16_REAL = 4,  /* 1 * 16bit unsigned int per sample */
#	AIRSPY_SAMPLE_RAW = 5,          /* Raw packed samples from the device */
#	AIRSPY_SAMPLE_END = 6           /* Number of supported sample types */
#};
# Define the types we need.
class CtypesEnum(enum.IntEnum):
    """A ctypes-compatible IntEnum superclass."""
    @classmethod
    def from_param(cls, obj):
        return int(obj)

class airspy_sample_type(enum.IntEnum):
	AIRSPY_SAMPLE_FLOAT32_IQ = 0   #/* 2 * 32bit float per sample */
	AIRSPY_SAMPLE_FLOAT32_REAL = 1 #/* 1 * 32bit float per sample */
	AIRSPY_SAMPLE_INT16_IQ = 2     #/* 2 * 16bit int per sample */
	AIRSPY_SAMPLE_INT16_REAL = 3   #/* 1 * 16bit int per sample */
	AIRSPY_SAMPLE_UINT16_REAL = 4  #/* 1 * 16bit unsigned int per sample */
	AIRSPY_SAMPLE_RAW = 5          #/* Raw packed samples from the device */
	AIRSPY_SAMPLE_END = 6          #/* Number of supported sample types */


class airspy_error(enum.IntEnum):
	AIRSPY_SUCCESS = 0
	AIRSPY_TRUE = 1
	AIRSPY_ERROR_INVALID_PARAM = -2
	AIRSPY_ERROR_NOT_FOUND = -5
	AIRSPY_ERROR_BUSY = -6
	AIRSPY_ERROR_NO_MEM = -11
	AIRSPY_ERROR_UNSUPPORTED = -12
	AIRSPY_ERROR_LIBUSB = -1000
	AIRSPY_ERROR_THREAD = -1001
	AIRSPY_ERROR_STREAMING_THREAD_ERR = -1002
	AIRSPY_ERROR_STREAMING_STOPPED = -1003
	AIRSPY_ERROR_OTHER = -9999

class airspy_board_id(enum.IntEnum):
	AIRSPY_BOARD_ID_PROTO_AIRSPY  = 0
	AIRSPY_BOARD_ID_INVALID = 0xFF

airspy_device_t_p = c_void_p

#typedef struct {
#	struct airspy_device* device;
#	void* ctx;
#	void* samples;
#	int sample_count;
#	uint64_t dropped_samples;
#	enum airspy_sample_type sample_type;
#} airspy_transfer_t, airspy_transfer;
class StructureWithEnums(Structure):
    """Add missing enum feature to ctypes Structures.
    """
    _map = {}

    def __getattribute__(self, name):
        _map = ctypes.Structure.__getattribute__(self, '_map')
        value = ctypes.Structure.__getattribute__(self, name)
        if name in _map:
            EnumClass = _map[name]
            if isinstance(value, ctypes.Array):
                return [EnumClass(x) for x in value]
            else:
                return EnumClass(value)
        else:
            return value

    def __str__(self):
        result = []
        result.append("struct {0} {{".format(self.__class__.__name__))
        for field in self._fields_:
            attr, attrType = field
            if attr in self._map:
                attrType = self._map[attr]
            value = getattr(self, attr)
            result.append("    {0} [{1}] = {2!r};".format(attr, attrType.__name__, value))
        result.append("};")
        return '\n'.join(result)

    __repr__ = __str__

#structures with enum
#https://gist.github.com/christoph2/9c390e5c094796903097
class airspy_transfer_t(Structure):
    _fields_ = [("device",airspy_device_t_p),
                ("ctx",c_void_p),
                ("samples",c_void_p),
                ("sample_count",c_int),
                ("dropped_samples",c_uint64),
                ("sample_type",c_int)]
                #]
    _map_ = {
    	"samples":airspy_sample_type
    }
                
airspy_transfer_t_p = POINTER(airspy_transfer_t)

#typedef struct {
#	uint32_t part_id[2];
#	uint32_t serial_no[4];
#} airspy_read_partid_serialno_t;
class airspy_read_partid_serialno_t(Structure):
    _fields_ = [("part_id", c_uint32*2),
                ("serial_no", c_uint32*4)]


#typedef struct {
#	uint32_t major_version;
#	uint32_t minor_version;
#	uint32_t revision;
#} airspy_lib_version_t;
class airspy_lib_version_t(Structure):
    _fields_ = [("major_version", c_uint32),
                ("minor_version", c_uint32),
                ("revision",      c_uint32)]



#typedef int (*airspy_sample_block_cb_fn)(airspy_transfer* transfer);
airspy_sample_block_cb_fn = PYFUNCTYPE(c_int, POINTER(airspy_transfer_t))


#extern ADDAPI void ADDCALL airspy_lib_version(airspy_lib_version_t* lib_version);
f = libairspy.airspy_lib_version
f.restype, f.argtypes = None, [POINTER(airspy_lib_version_t)]

#try to load the lib version if its wrong print out warning
version = airspy_lib_version_t()
libairspy.airspy_lib_version(byref(version))
if False == ((int(version.major_version) == 1) and (int(version.minor_version) == 0) and (int(version.revision) == 11)):
    print("Unsuported version of libairspy.")
    print("Only supporting 1.0.11")
    raise ImportError

#/* airspy_init() deprecated */
#extern ADDAPI int ADDCALL airspy_init(void);
#/* airspy_exit() deprecated */
#extern ADDAPI int ADDCALL airspy_exit(void);

#extern ADDAPI int ADDCALL airspy_list_devices(uint64_t *serials, int count);
f = libairspy.airspy_list_devices
f.restype, f.argtypes = c_int, [POINTER(c_uint64), c_int]

#extern ADDAPI int ADDCALL airspy_open_sn(struct airspy_device** device, uint64_t serial_number);
f = libairspy.airspy_open_sn
f.restype, f.argtypes = c_int, [POINTER(airspy_device_t_p), c_uint64]

#extern ADDAPI int ADDCALL airspy_open_fd(struct airspy_device** device, int fd);
f = libairspy.airspy_open_fd
f.restype, f.argtypes = c_int, [POINTER(airspy_device_t_p), c_int]

#extern ADDAPI int ADDCALL airspy_open(struct airspy_device** device);
f = libairspy.airspy_open
f.restype, f.argtypes = c_int, [POINTER(airspy_device_t_p)]

#extern ADDAPI int ADDCALL airspy_close(struct airspy_device* device);
f = libairspy.airspy_close
f.restype, f.argtypes = c_int, [airspy_device_t_p]

#/* Use airspy_get_samplerates(device, buffer, 0) to get the number of available sample rates. It will be returned in the first element of buffer */
#extern ADDAPI int ADDCALL airspy_get_samplerates(struct airspy_device* device, uint32_t* buffer, const uint32_t len);
f = libairspy.airspy_get_samplerates
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(c_uint32), c_uint32]


#/* Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list returned by airspy_get_samplerates() */
#extern ADDAPI int ADDCALL airspy_set_samplerate(struct airspy_device* device, uint32_t samplerate);
f = libairspy.airspy_set_samplerate
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint32]


#extern ADDAPI int ADDCALL airspy_set_conversion_filter_float32(struct airspy_device* device, const float *kernel, const uint32_t len);
f = libairspy.airspy_set_conversion_filter_float32
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(c_float), c_uint32]

#extern ADDAPI int ADDCALL airspy_set_conversion_filter_int16(struct airspy_device* device, const int16_t *kernel, const uint32_t len);
f = libairspy.airspy_set_conversion_filter_int16
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(c_int16), c_uint32]

#extern ADDAPI int ADDCALL airspy_start_rx(struct airspy_device* device, airspy_sample_block_cb_fn callback, void* rx_ctx);
f = libairspy.airspy_start_rx
f.restype, f.argtypes = c_int, [airspy_device_t_p, airspy_sample_block_cb_fn, py_object]

#extern ADDAPI int ADDCALL airspy_stop_rx(struct airspy_device* device);
f = libairspy.airspy_stop_rx
f.restype, f.argtypes = c_int, [airspy_device_t_p]

#/* return AIRSPY_TRUE if success */
#extern ADDAPI int ADDCALL airspy_is_streaming(struct airspy_device* device);
f = libairspy.airspy_is_streaming
f.restype, f.argtypes = c_int, [airspy_device_t_p]

#extern ADDAPI int ADDCALL airspy_si5351c_write(struct airspy_device* device, uint8_t register_number, uint8_t value);
f = libairspy.airspy_set_conversion_filter_float32
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(c_float), c_uint32]

#extern ADDAPI int ADDCALL airspy_si5351c_read(struct airspy_device* device, uint8_t register_number, uint8_t* value);
f = libairspy.airspy_si5351c_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8, POINTER(c_uint8)]

#extern ADDAPI int ADDCALL airspy_config_write(struct airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data);
#f = libairspy.airspy_config_write
#f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8, c_uint16, c_char_p]

#extern ADDAPI int ADDCALL airspy_config_read(struct airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data);
#f = libairspy.airspy_config_read
#f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8, c_uint16, c_ubyte_p]

#extern ADDAPI int ADDCALL airspy_r820t_write(struct airspy_device* device, uint8_t register_number, uint8_t value);
#f = libairspy.airspy_r820t_write
#f.restype, f.argtypes = c_int, [airspy_device_t_p. c_uint8, c_uint8]

#extern ADDAPI int ADDCALL airspy_r820t_read(struct airspy_device* device, uint8_t register_number, uint8_t* value);
f = libairspy.airspy_r820t_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8, POINTER(c_uint8)]

#/* Parameter value shall be 0=clear GPIO or 1=set GPIO */
#extern ADDAPI int ADDCALL airspy_gpio_write(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t value);
#f = libairspy.airspy_gpio_write
#f.restype, f.argtypes = c_int, [airspy_device_t_p]

#/* Parameter value corresponds to GPIO state 0 or 1 */
#extern ADDAPI int ADDCALL airspy_gpio_read(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t* value);
#f = libairspy.airspy_gpio_read
#f.restype, f.argtypes = c_int, [airspy_device_t_p]

#/* Parameter value shall be 0=GPIO Input direction or 1=GPIO Output direction */
#extern ADDAPI int ADDCALL airspy_gpiodir_write(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t value);
#f = libairspy.airspy_gpiodir_write
#f.restype, f.argtypes = c_int, [airspy_device_t_p]
#extern ADDAPI int ADDCALL airspy_gpiodir_read(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t* value);
#f = libairspy.airspy_gpiodir_read
#f.restype, f.argtypes = c_int, [airspy_device_t_p]

#extern ADDAPI int ADDCALL airspy_spiflash_erase(struct airspy_device* device);
f = libairspy.airspy_spiflash_erase
f.restype, f.argtypes = c_int, [airspy_device_t_p]

#extern ADDAPI int ADDCALL airspy_spiflash_write(struct airspy_device* device, const uint32_t address, const uint16_t length, unsigned char* const data);
f = libairspy.airspy_spiflash_write
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint32, c_uint16, POINTER(c_ubyte)]

#extern ADDAPI int ADDCALL airspy_spiflash_read(struct airspy_device* device, const uint32_t address, const uint16_t length, unsigned char* data);
f = libairspy.airspy_spiflash_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint32, c_uint16, POINTER(c_ubyte)]

#extern ADDAPI int ADDCALL airspy_board_id_read(struct airspy_device* device, uint8_t* value);
f = libairspy.airspy_board_id_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(c_uint8)]

#/* Parameter length shall be at least 128bytes to avoid possible string clipping */
#extern ADDAPI int ADDCALL airspy_version_string_read(struct airspy_device* device, char* version, uint8_t length);
f = libairspy.airspy_version_string_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_char_p, c_uint8]

#extern ADDAPI int ADDCALL airspy_board_partid_serialno_read(struct airspy_device* device, airspy_read_partid_serialno_t* read_partid_serialno);
f = libairspy.airspy_board_partid_serialno_read
f.restype, f.argtypes = c_int, [airspy_device_t_p, POINTER(airspy_read_partid_serialno_t)]

#extern ADDAPI int ADDCALL airspy_set_sample_type(struct airspy_device* device, enum airspy_sample_type sample_type);
f = libairspy.airspy_set_sample_type
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_int]

#/* Parameter freq_hz shall be between 24000000(24MHz) and 1750000000(1.75GHz) */
#extern ADDAPI int ADDCALL airspy_set_freq(struct airspy_device* device, const uint32_t freq_hz);
f = libairspy.airspy_set_freq
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint32]

#/* Parameter value shall be between 0 and 15 */
#extern ADDAPI int ADDCALL airspy_set_lna_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_lna_gain
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value shall be between 0 and 15 */
#extern ADDAPI int ADDCALL airspy_set_mixer_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_mixer_gain
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]


#/* Parameter value shall be between 0 and 15 */
#extern ADDAPI int ADDCALL airspy_set_vga_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_vga_gain
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value:
#	0=Disable LNA Automatic Gain Control
#	1=Enable LNA Automatic Gain Control
#*/
#extern ADDAPI int ADDCALL airspy_set_lna_agc(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_lna_agc
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value:
#	0=Disable MIXER Automatic Gain Control
#	1=Enable MIXER Automatic Gain Control
#*/
#extern ADDAPI int ADDCALL airspy_set_mixer_agc(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_mixer_agc
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value: 0..21 */
#extern ADDAPI int ADDCALL airspy_set_linearity_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_linearity_gain
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value: 0..21 */
#extern ADDAPI int ADDCALL airspy_set_sensitivity_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_sensitivity_gain
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value shall be 0=Disable BiasT or 1=Enable BiasT */
#extern ADDAPI int ADDCALL airspy_set_rf_bias(struct airspy_device* dev, uint8_t value);
f = libairspy.airspy_set_rf_bias
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#/* Parameter value shall be 0=Disable Packing or 1=Enable Packing */
#extern ADDAPI int ADDCALL airspy_set_packing(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_packing
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint8]

#extern ADDAPI const char* ADDCALL airspy_error_name(enum airspy_error errcode);
#f = libairspy.airspy_error_name
#f.restype, f.argtypes = c_char_p, []

#extern ADDAPI const char* ADDCALL airspy_board_id_name(enum airspy_board_id board_id);
#f = libairspy.airspy_board_id_name
#f.restype, f.argtypes = c_char_p, [airspy_device_t_p]

#/* Parameter sector_num shall be between 2 & 13 (sector 0 & 1 are reserved) */
#extern ADDAPI int ADDCALL airspy_spiflash_erase_sector(struct airspy_device* device, const uint16_t sector_num);
f = libairspy.airspy_spiflash_erase_sector
f.restype, f.argtypes = c_int, [airspy_device_t_p, c_uint16]


