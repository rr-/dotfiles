require 'mp.options'

local options = {
  visible = true,
  margin_x = 10,
  margin_y = 10,
  w = 150,
  h = 150,
}
read_options(options, 'crop_view')

local osd1 = mp.create_osd_overlay("ass-events")
local osd2 = mp.create_osd_overlay("ass-events")

function make_ass_rect(x, y, color, rect)
  local x0 = rect.x0
  local y0 = rect.y0
  local x1 = rect.x1
  local y1 = rect.y1
  return string.format(
    "{\\an7\\pos(%d,%d)\\shad0\\blur0\\be0\\bord1\\1a&HFF&\\3c&H%s&\\p1}" ..
    "m %d %d l %d %d l %d %d l %d %d l %d %d{\\p0}",
    x, y, color, x0, y0, x1, y0, x1, y1, x0, y1, x0, y0)
end

function get_viewport_rect(opts)
  local w = options.w
  local h = options.h

  local window_w = opts.window_w * (1 - opts.margin_x[1] - opts.margin_x[2])
  local window_h = opts.window_h * (1 - opts.margin_y[1] - opts.margin_y[2])

  local screen_aspect = window_w / window_h
  local viewport_aspect = w / h
  if screen_aspect > viewport_aspect then
    h = h / screen_aspect
  else
    w = w * screen_aspect
  end

  return { x0 = 0, y0 = 0, x1 = w, y1 = h }
end

function adjust_rect(subject, src_rect, dst_rect)
  local scale_x = (dst_rect.x1 - dst_rect.x0) / (src_rect.x1 - src_rect.x0)
  local scale_y = (dst_rect.y1 - dst_rect.y0) / (src_rect.y1 - src_rect.y0)
  return {
    x0 = dst_rect.x0 + (subject.x0 - src_rect.x0) * scale_x,
    y0 = dst_rect.y0 + (subject.y0 - src_rect.y0) * scale_y,
    x1 = dst_rect.x1 + (subject.x1 - src_rect.x1) * scale_x,
    y1 = dst_rect.y1 + (subject.y1 - src_rect.y1) * scale_y,
  }
end

function update()
  if not options.visible then
    osd1.data = ''
    osd2.data = ''
    osd1:update()
    osd2:update()
    return
  end

  local video_params = {
    w = mp.get_property_number("dwidth"),
    h = mp.get_property_number("dheight"),
    rotate = mp.get_property_native("video-rotate"), -- TODO: support rotations
  }

  local osd_w, osd_h, osd_ar = mp.get_osd_size()
  local opts = {
    monitor_par = 1,
    keepaspect = mp.get_property_native("keepaspect"),
    margin_x = {
      mp.get_property_native("video-margin-ratio-left"),
      mp.get_property_native("video-margin-ratio-right"),
    },
    margin_y = {
      mp.get_property_number("video-margin-ratio-top", 0),
      mp.get_property_number("video-margin-ratio-bottom", 0),
    },
    unscaled = mp.get_property_native("video-unscaled"),
    zoom = mp.get_property_number("video-zoom", 0),
    align_x = mp.get_property_number("align-x", 0),
    align_y = mp.get_property_number("align-y", 0),
    pan_x = mp.get_property_number("video-pan-x", 0),
    pan_y = mp.get_property_number("video-pan-y", 0),
    panscan = mp.get_property_native("panscan"),
    scale_x = mp.get_property_number("scale-x", 1),
    scale_y = mp.get_property_number("scale-x", 1),
    window_w = mp.get_property_native("display-width"),
    window_h = mp.get_property_native("display-height"),
    play_res_x = 720 * osd_ar,
    play_res_y = 720,
    osd_margin_x = mp.get_property_native("osd-margin-x"),
    osd_margin_y = mp.get_property_native("osd-margin-y"),
  }

  if opts.window_w == nil or video_params.w == nil then
    return
  end

  local src_rect, dst_rect, osd = get_src_dst_rects(video_params, opts)
  local video_rect = {x0 = 0, y0 = 0, x1 = video_params.w, y1 = video_params.h}
  local viewport_rect = get_viewport_rect(opts)
  local adjusted_src_rect = adjust_rect(src_rect, video_rect, viewport_rect)

  local target_x = opts.play_res_x + opts.osd_margin_x - options.margin_x - math.abs(viewport_rect.x1 - viewport_rect.x0)
  local target_y = opts.play_res_y + opts.osd_margin_y - options.margin_y - math.abs(viewport_rect.y1 - viewport_rect.y0)
  osd1.data = make_ass_rect(target_x, target_y, "FFFFFF", viewport_rect)
  osd2.data = make_ass_rect(target_x, target_y, "00FFFF", adjusted_src_rect)
  osd1:update()
  osd2:update()
end

function calculate_margins(opts_array, margin_array, length)
  margin_array[1] = math.floor(opts_array[1] * length)
  margin_array[2] = math.floor(opts_array[2] * length)
end

function aspect_calc_panscan(opts, w, h, d_w, d_h, window_w, window_h)
  local f_width = window_w
  local f_height = window_w / d_w * d_h / opts.monitor_par
  if f_height > window_h or f_height < h then
    local tmpw = window_h / d_h * d_w * opts.monitor_par
    if tmpw <= window_w then
      f_height = window_h
      f_width = tmpw
    end
  end

  local vo_panscan_area = window_h - f_height
  local f_w = f_width / math.max(f_height, 1)
  local f_h = 1
  if vo_panscan_area == 0 then
    vo_panscan_area = window_w - f_width
    f_w = 1
    f_h = f_height / math.max(f_width, 1)
  end

  if opts.unscaled then
    vo_panscan_area = 0
    if opts.unscaled ~= 2 or (d_w <= window_w and d_h <= window_h) then
      f_width = d_w * opts.monitor_par
      f_height = d_h
    end
  end

  local out_w = f_width + vo_panscan_area * opts.panscan * f_w
  local out_h = f_height + vo_panscan_area * opts.panscan * f_h
  return out_w, out_h
end

function src_dst_split_scaling(
  src_size,
  dst_size,
  scaled_src_size,
  zoom,
  align,
  pan,
  scale,
  src_start,
  src_end
)
  local scaled_src_size = scaled_src_size * (2 ^ zoom) * scale
  scaled_src_size = math.max(scaled_src_size, 1)
  align = (align + 1) / 2

  local dst_start = (dst_size - scaled_src_size) * align + pan * scaled_src_size
  local dst_end = dst_start + scaled_src_size

  -- Distance of screen frame to video
  local osd_margin_a = dst_start
  local osd_margin_b = dst_size - dst_end

  -- Clip to screen
  local s_src = src_end - src_start
  local s_dst = dst_end - dst_start
  if dst_start < 0 then
    local border = -(dst_start) * s_src / s_dst
    src_start = src_start + border
    dst_start = 0
  end
  if dst_end > dst_size then
    local border = (dst_end - dst_size) * s_src / s_dst
    src_end = src_end - border
    dst_end = dst_size
  end

  -- For sanity: avoid bothering VOs with corner cases
  -- clamp_size(src_size, src_start, src_end)
  -- clamp_size(dst_size, dst_start, dst_end)

  return src_start, src_end, dst_start, dst_end, osd_margin_a, osd_margin_b
end

function get_src_dst_rects(video_params, opts)
  local out_src = {}
  local out_dst = {}
  local out_osd = {}

  local src_w = video_params.w
  local src_h = video_params.h
  local src_dw = video_params.w
  local src_dh = video_params.h
  local window_w = math.max(1, opts.window_w)
  local window_h = math.max(1, opts.window_h)
  local margin_x = {0, 0}
  local margin_y = {0, 0}
  if opts.keepaspect then
    calculate_margins(opts.margin_x, margin_x, window_w)
    calculate_margins(opts.margin_y, margin_y, window_h)
  end
  local vid_window_w = window_w - margin_x[1] - margin_x[2]
  local vid_window_h = window_h - margin_y[1] - margin_y[2]

  local dst = {x0 = 0, y0 = 0, x1 = window_w, y1 = window_h}
  local src = {x0 = 0, y0 = 0, x1 = src_w, y1 = src_h}
  local osd = {
    w = window_w,
    h = window_h,
    display_par = monitor_par,
    ml = 0,
    mr = 0,
    mt = 0,
    mb = 0
}

  if opts.keepaspect then
    scaled_width, scaled_height = aspect_calc_panscan(
      opts, src_w, src_h, src_dw, src_dh, vid_window_w, vid_window_h)

    src.x0, src.x1, dst.x0, dst.x1, osd.ml, osd.mr = src_dst_split_scaling(
      src_w,
      vid_window_w,
      scaled_width,
      opts.zoom,
      opts.align_x,
      opts.pan_x,
      opts.scale_x,
      src.x0,
      src.x1)

    src.y0, src.y1, dst.y0, dst.y1, osd.mt, osd.mb = src_dst_split_scaling(
      src_h,
      vid_window_h,
      scaled_height,
      opts.zoom,
      opts.align_y,
      opts.pan_y,
      opts.scale_y,
      src.y0,
      src.y1)
  end

  dst.x0 = dst.x0 + margin_x[1]
  dst.y0 = dst.y0 + margin_y[1]
  dst.x1 = dst.x1 + margin_x[1]
  dst.y1 = dst.y1 + margin_y[1]

  osd.ml = osd.ml + margin_x[1]
  osd.mr = osd.mr + margin_x[2]
  osd.mt = osd.mt + margin_y[1]
  osd.mb = osd.mb + margin_y[2]

  return src, dst, osd
end

function change_margin_x(margin_x)
  options.margin_x = tonumber(margin_x)
  update()
end

function change_margin_y(margin_y)
  options.margin_y = tonumber(margin_y)
  update()
end

function toggle()
  options.visible = not options.visible
  update()
end

mp.observe_property("video-pan-x", "native", update)
mp.observe_property("video-pan-y", "native", update)
mp.observe_property("video-zoom", "native", update)
mp.observe_property("video-unscaled", "native", update)
mp.observe_property("panscan", "native", update)
mp.observe_property("dwidth", "native", update)
mp.register_script_message('change-margin-x', change_margin_x)
mp.register_script_message('change-margin-y', change_margin_y)
mp.register_script_message('update', update)
mp.register_script_message('toggle', toggle)

update()
