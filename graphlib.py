def draw_graph(data, description, bins_count=100):
    height_chars = "▁▂▃▄▅▆▇█"
    
    if len(data) == bins_count:
        binned_data = data
    elif len(data) > bins_count:
        bin_size = len(data) / bins_count
        binned_data = []
        # Compute the average for each bin
        for i in range(bins_count):
            start_idx = int(i * bin_size)
            end_idx = int((i + 1) * bin_size) if i != bins_count - 1 else len(data)
            avg = sum(data[start_idx:end_idx]) / (end_idx - start_idx) if (end_idx - start_idx) != 0 else 0
            binned_data.append(avg)
    else:  # Stretching the data using nearest neighbor mapping
        binned_data = [data[int(i * (len(data) - 1) / (bins_count - 1) + 0.5)] for i in range(bins_count)]
    
    min_val, max_val = min(binned_data), max(binned_data)

    if min_val == max_val:
        print(height_chars[-1] * bins_count + " " + description)
        return

    normalized_binned_data = [(x - min_val) / (max_val - min_val) * (len(height_chars) - 1) for x in binned_data]
    normalized_binned_data = [max(0, min(len(height_chars) - 1, round(val))) for val in normalized_binned_data]

    graph = ''.join([height_chars[int(val)] for val in normalized_binned_data])

    print(f"{description}:\n [{graph}]\n")

def test_draw_graph():
    draw_graph([1, 2, 3, 4, 5, 6, 7, 8], "Expected: ▁▂▃▄▅▆▇█", 8)
    draw_graph([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "Expected: ▁▂▃▄▅▆▇█", 8)
    draw_graph([1, 2, 3], "Expected: ▁▅█", 3)
    draw_graph([1, 2, 3], "Expected: ▁▁▅▅██", 6)
    draw_graph([1, 2, 3], "Expected: ▁▁▁▅▅▅███", 9)
    draw_graph([1, 1, 1], "Expected: ███████", 7)
    draw_graph([1], "Expected: ███████", 7)
    draw_graph([1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1], "Expected: ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁", 15)
    draw_graph([i for i in range(1,101)], "Expected: ▁▂▃▄▅▆▇█", 8)
    draw_graph([99]+[100]*99, "Expected: ▁███████", 8)
    draw_graph([99]+[100]*99, "Expected: ▁███████████████████████████████████████████████████████████████████████████████████████████████████", 100)

#test_draw_graph()
