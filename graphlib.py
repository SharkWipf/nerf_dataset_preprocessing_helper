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
    else:  # Stretching the data by replicating the data points
        repetitions = bins_count // len(data)
        binned_data = []
        for val in data:
            binned_data.extend([val] * repetitions)
        # Add the remaining bins if any
        binned_data.extend([data[-1]] * (bins_count - len(binned_data)))

    min_val, max_val = min(binned_data), max(binned_data)

    if min_val == max_val:
        min_val = min_val - 1

    normalized_binned_data = [(x - min_val) / (max_val - min_val) * (len(height_chars) - 1) for x in binned_data]
    normalized_binned_data = [max(0, min(len(height_chars) - 1, round(val))) for val in normalized_binned_data]

    graph = ''.join([height_chars[int(val)] for val in normalized_binned_data])

    print(f"{description}:\n [{graph}]\n")


def test_draw_graph():
    tests = [
        ([1, 2, 3, 4, 5, 6, 7, 8], "[▁▂▃▄▅▆▇█]", 8),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "[▁▂▃▄▅▆▇█]", 8),
        ([1, 2, 3], "[▁▅█]", 3),
        ([1, 2, 3], "[▁▁▅▅██]", 6),
        ([1, 2, 3], "[▁▁▁▅▅▅███]", 9),
        ([1, 1, 1], "[███████]", 7),
        ([1], "[███████]", 7),
        ([1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1], "[▁▂▃▄▅▆▇█▇▆▅▄▃▂▁]", 15),
        ([i for i in range(1,101)], "[▁▂▃▄▅▆▇█]", 8),
        ([99]+[100]*99, "[▁███████]", 8),
        ([99]+[100]*99, "[▁███████████████████████████████████████████████████████████████████████████████████████████████████]", 100),
        ([1,0,1,0], "[█████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁]", 100)
    ]

    for i, (data, expected, bins) in enumerate(tests, 1):
        description = f"{i}. {data}, {bins} bins. Expectation: \n {expected}\nReality"
        draw_graph(data, description, bins)


#test_draw_graph()
