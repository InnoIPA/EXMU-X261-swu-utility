--[[
     Copyright (c) 2023 Innodisk Crop.

     This software is released under the MIT License.
     https://opensource.org/licenses/MIT
]]


-- https://github.com/sbabic/swupdate/blob/2023.05/handlers/swupdate.lua

require('swupdate')

--- Lua Handler.
--
--- @param  image  img_type  Lua equivalent of `struct img_type`
--- @return number           # 0 on success, 1 on error
function boot_bin_handler(image)
    swupdate.progress_update(1)
    os.execute("flash_lock -u /dev/mtd2")

    swupdate.progress_update(30)
    local image = swupdate.tmpdir() .. image.filename
    local _,_,code = os.execute("image_update -i " .. image)

    swupdate.progress_update(100)
    return code
end

swupdate.register_handler("boot_bin", boot_bin_handler, swupdate.HANDLER_MASK.IMAGE_HANDLER)


--- Lua Handler.
--
--- @param  image  img_type  Lua equivalent of `struct img_type`
--- @return number           # 0 on success, 1 on error
function rpm_handler(image)
    swupdate.progress_update(1)
    swupdate.progress_update(30)

    local image = swupdate.tmpdir() .. image.filename
    local _,_,code = os.execute("rpm -ivh --force " .. image)

    swupdate.progress_update(100)
    return code
end

swupdate.register_handler("rpm", rpm_handler, swupdate.HANDLER_MASK.IMAGE_HANDLER)
