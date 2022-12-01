#bash

for f in ./.tmp/logs/*; do
    results=${f/.tmp/.results}
    echo "Comparing $f and $results"
    diff -a <(sort $f) <(sort $results)
done

# Check files
for f in ./.tmp/*; do
    if [[ "$f" == *"client"* ]]; then
        results=${f/.tmp/.results}
        echo "Comparing $f and $results"

        diff -qr $f $results
    fi
done